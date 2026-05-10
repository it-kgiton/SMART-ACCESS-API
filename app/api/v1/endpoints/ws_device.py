"""
WebSocket endpoint for fingerprint device communication.

Protocol (from ESP32 firmware):
  Device → Server:
    {"event":"connected","license_key":"...","firmware":"5.2.0"}
    {"event":"enroll_ok","customer_id":"...","finger_id":N,"template":"base64..."}
    {"event":"verify_request"}
    {"event":"verify_ok","finger_id":N,"confidence":M,"customer_id":"..."}
    {"event":"verify_fail","error":"..."}
    {"event":"error","error":"..."}
    {"event":"status",...}

  Server → Device:
    {"cmd":"enroll","customer_id":"xxx","finger_index":1}
    {"cmd":"verify"}
    {"cmd":"verify_templates","batch":1,"templates":[...],"has_more":true}
    {"cmd":"cancel"}
    {"cmd":"ping"}
    {"cmd":"status"}
"""

import json
import asyncio
import base64
from typing import Dict, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from loguru import logger

from app.core.database import AsyncSessionLocal
from app.models.device import Device, DeviceStatus
from app.models.biometric import FingerprintCredential, CredentialStatus
from app.models.client import Client
from app.services.enrollment_service import EnrollmentService


router = APIRouter()


class DeviceConnectionManager:
    """Manages active WebSocket connections from fingerprint devices."""
    
    def __init__(self):
        # license_key -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # license_key -> device info (from "connected" event)
        self.device_info: Dict[str, dict] = {}
        # license_key -> list of dashboard websockets watching this device
        self.dashboard_watchers: Dict[str, list] = {}
        # license_key -> enrollment start timestamp (None = not enrolling)
        self.active_enrollment: Dict[str, float] = {}
    
    async def connect(self, license_key: str, websocket: WebSocket) -> bool:
        """Accept device connection if license_key is registered."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Device).where(
                    Device.license_key == license_key,
                    Device.is_active.is_(True)
                )
            )
            device = result.scalar_one_or_none()
            
            if not device:
                logger.warning(f"[WS] Rejected: license_key={license_key} not found")
                return False
            
            await websocket.accept()
            self.active_connections[license_key] = websocket
            
            # Update device status
            device.status = DeviceStatus.ACTIVE
            device.last_heartbeat = datetime.now(timezone.utc)
            await db.commit()
            
            logger.info(f"[WS] Device connected: {license_key}")
            return True
    
    def disconnect(self, license_key: str):
        """Handle device disconnection."""
        if license_key in self.active_connections:
            del self.active_connections[license_key]
        if license_key in self.device_info:
            del self.device_info[license_key]
        self.clear_enrollment(license_key)
        logger.info(f"[WS] Device disconnected: {license_key}")
        
        # Notify dashboard watchers
        asyncio.create_task(self._notify_watchers(license_key, {
            "event": "device_offline",
            "license_key": license_key
        }))

    def start_enrollment(self, license_key: str):
        """Mark a device as currently enrolling."""
        self.active_enrollment[license_key] = datetime.now(timezone.utc).timestamp()

    def clear_enrollment(self, license_key: str):
        """Clear enrollment tracking for a device."""
        self.active_enrollment.pop(license_key, None)

    def is_enrolling(self, license_key: str) -> bool:
        """Return True if device has an enrollment in progress (max 120s TTL)."""
        ts = self.active_enrollment.get(license_key)
        if ts is None:
            return False
        if (datetime.now(timezone.utc).timestamp() - ts) > 45:
            self.active_enrollment.pop(license_key, None)
            return False
        return True
    
    def is_connected(self, license_key: str) -> bool:
        return license_key in self.active_connections
    
    def get_connection(self, license_key: str) -> Optional[WebSocket]:
        return self.active_connections.get(license_key)
    
    def set_device_info(self, license_key: str, info: dict):
        self.device_info[license_key] = info
    
    def get_device_info(self, license_key: str) -> Optional[dict]:
        return self.device_info.get(license_key)
    
    def get_all_connected(self) -> list:
        """Return list of all connected device license keys."""
        return list(self.active_connections.keys())
    
    async def send_command(self, license_key: str, command: dict) -> bool:
        """Send command to device."""
        ws = self.active_connections.get(license_key)
        if not ws:
            return False
        try:
            await ws.send_json(command)
            return True
        except Exception as e:
            logger.error(f"[WS] Send failed to {license_key}: {e}")
            return False
    
    # Dashboard watcher management
    def add_watcher(self, license_key: str, ws: WebSocket):
        if license_key not in self.dashboard_watchers:
            self.dashboard_watchers[license_key] = []
        self.dashboard_watchers[license_key].append(ws)
    
    def remove_watcher(self, license_key: str, ws: WebSocket):
        if license_key in self.dashboard_watchers:
            try:
                self.dashboard_watchers[license_key].remove(ws)
            except ValueError:
                pass
    
    async def _notify_watchers(self, license_key: str, data: dict):
        """Forward device events to dashboard watchers."""
        watchers = self.dashboard_watchers.get(license_key, [])
        for ws in watchers[:]:  # copy to avoid mutation during iteration
            try:
                await ws.send_json(data)
            except:
                self.remove_watcher(license_key, ws)
    
    async def forward_to_watchers(self, license_key: str, event_data: dict):
        """Forward device event to all dashboard watchers."""
        await self._notify_watchers(license_key, event_data)


async def _send_verify_templates(license_key: str) -> None:
    """
    Fetch all active fingerprint templates for the device's school and
    send them to the device in batches as verify_templates commands.
    """
    BATCH_SIZE = 5
    try:
        async with AsyncSessionLocal() as db:
            # Get device to find school_id
            dev_result = await db.execute(
                select(Device).where(Device.license_key == license_key)
            )
            device = dev_result.scalar_one_or_none()
            if not device:
                logger.warning(f"[WS] verify_request: device not found for {license_key}")
                return

            # Fetch all active fingerprint credentials for this school
            cred_result = await db.execute(
                select(FingerprintCredential)
                .join(Client, Client.id == FingerprintCredential.client_id)
                .where(Client.school_id == device.school_id)
                .where(FingerprintCredential.status == CredentialStatus.ACTIVE)
            )
            creds = cred_result.scalars().all()

        total = len(creds)
        logger.info(f"[WS] Sending {total} templates to {license_key} for verify")

        if total == 0:
            await device_manager.send_command(license_key, {
                "cmd": "verify_templates",
                "batch": 1, "total_batches": 1, "has_more": False,
                "templates": []
            })
            return

        total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
        for batch_num in range(1, total_batches + 1):
            start = (batch_num - 1) * BATCH_SIZE
            batch = creds[start:start + BATCH_SIZE]
            templates = [
                {
                    "slot": start + i + 1,
                    "customer_id": cred.client_id,
                    "template": base64.b64encode(cred.template_data).decode()
                }
                for i, cred in enumerate(batch)
            ]
            await device_manager.send_command(license_key, {
                "cmd": "verify_templates",
                "batch": batch_num,
                "total_batches": total_batches,
                "has_more": batch_num < total_batches,
                "templates": templates
            })
    except Exception as exc:
        logger.error(f"[WS] Failed to send verify templates to {license_key}: {exc}")


# Global connection manager
device_manager = DeviceConnectionManager()


@router.websocket("/ws/device/{license_key}")
async def device_websocket(websocket: WebSocket, license_key: str):
    """
    WebSocket endpoint for fingerprint devices.
    Device connects with license_key in URL path.
    """
    # Validate and accept connection
    if not await device_manager.connect(license_key, websocket):
        await websocket.close(code=4003, reason="Device not registered")
        return
    
    try:
        while True:
            # Receive message from device (may be text or binary frame)
            raw = await websocket.receive()
            if raw.get("type") == "websocket.disconnect":
                raise WebSocketDisconnect(code=raw.get("code", 1000))
            if raw.get("bytes") is not None:
                # Binary frame (e.g. fingerprint image after enroll_image) — just consume
                continue
            data = raw.get("text", "")
            if not data:
                continue
            
            try:
                msg = json.loads(data)
                event = msg.get("event")
                
                if event == "connected":
                    # Clear any stale enrollment lock from previous session
                    device_manager.clear_enrollment(license_key)
                    # Store device info
                    device_manager.set_device_info(license_key, {
                        "firmware": msg.get("firmware"),
                        "connected_at": datetime.now(timezone.utc).isoformat()
                    })
                    logger.info(f"[WS] Device {license_key} firmware={msg.get('firmware')}")
                    
                    # Notify watchers
                    await device_manager.forward_to_watchers(license_key, {
                        "event": "device_online",
                        "license_key": license_key,
                        "firmware": msg.get("firmware")
                    })
                
                elif event == "status":
                    # Update heartbeat
                    async with AsyncSessionLocal() as db:
                        result = await db.execute(
                            select(Device).where(Device.license_key == license_key)
                        )
                        device = result.scalar_one_or_none()
                        if device:
                            device.last_heartbeat = datetime.now(timezone.utc)
                            await db.commit()
                    
                    # Forward to watchers
                    await device_manager.forward_to_watchers(license_key, msg)
                
                elif event in ("enroll_start", "enroll_scan1", "enroll_scan1_ok", 
                               "enroll_scan2", "enroll_retry", "enroll_ok", 
                               "enroll_image", "error"):
                    if event == "enroll_ok":
                        device_manager.clear_enrollment(license_key)
                        template_b64 = msg.get("template")
                        client_id    = msg.get("customer_id")
                        finger_index = msg.get("finger_id", 1)
                        saved = False
                        if template_b64 and client_id:
                            try:
                                template_data = base64.b64decode(template_b64)
                                async with AsyncSessionLocal() as db:
                                    svc = EnrollmentService(db)
                                    await svc.enroll_fingerprint(client_id, template_data, finger_index)
                                saved = True
                                logger.info(f"[WS] Enroll saved: {license_key} customer={client_id} finger={finger_index}")
                            except Exception as exc:
                                logger.error(f"[WS] Failed to save fingerprint: {exc}")
                        else:
                            logger.warning(f"[WS] enroll_ok missing template or customer_id: {license_key}")
                        await device_manager.forward_to_watchers(license_key, {**msg, "saved": saved})
                    elif event == "error":
                        device_manager.clear_enrollment(license_key)
                        await device_manager.forward_to_watchers(license_key, msg)
                    else:
                        # Forward other enrollment events to watchers
                        await device_manager.forward_to_watchers(license_key, msg)
                
                elif event in ("verify_start", "verify_scan", "verify_processing",
                               "verify_request", "verify_batch_ok", "verify_ok", 
                               "verify_fail"):
                    # Forward verify events to watchers
                    await device_manager.forward_to_watchers(license_key, msg)
                    
                    if event == "verify_ok":
                        logger.info(f"[WS] Verify OK: {license_key} customer={msg.get('customer_id')} score={msg.get('confidence')}")
                    elif event == "verify_request":
                        # Device requesting templates — fetch from DB and send in batches
                        logger.info(f"[WS] Verify request from {license_key}")
                        asyncio.create_task(
                            _send_verify_templates(license_key)
                        )
                
                elif event == "pong":
                    pass  # Response to ping
                
                elif event == "cancelled":
                    await device_manager.forward_to_watchers(license_key, msg)
                
                else:
                    logger.debug(f"[WS] Unknown event from {license_key}: {event}")
                    await device_manager.forward_to_watchers(license_key, msg)
                    
            except json.JSONDecodeError:
                logger.warning(f"[WS] Invalid JSON from {license_key}: {data[:200]}")
                
    except WebSocketDisconnect:
        device_manager.disconnect(license_key)
        
        # Update device status to offline
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Device).where(Device.license_key == license_key)
            )
            device = result.scalar_one_or_none()
            if device:
                device.status = DeviceStatus.OFFLINE
                await db.commit()


@router.websocket("/ws/dashboard/device/{license_key}")
async def dashboard_device_websocket(websocket: WebSocket, license_key: str):
    """
    WebSocket for dashboard to watch a specific device's events.
    Used for real-time enrollment/verification UI updates.
    """
    await websocket.accept()
    device_manager.add_watcher(license_key, websocket)
    
    # Send current status
    if device_manager.is_connected(license_key):
        info = device_manager.get_device_info(license_key) or {}
        await websocket.send_json({
            "event": "device_online",
            "license_key": license_key,
            **info
        })
    else:
        await websocket.send_json({
            "event": "device_offline", 
            "license_key": license_key
        })
    
    try:
        while True:
            # Dashboard can send commands to device
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                cmd = msg.get("cmd")
                
                if cmd:
                    if cmd == "enroll":
                        if device_manager.is_enrolling(license_key):
                            await websocket.send_json({
                                "event": "error",
                                "error": "Device sedang dalam proses enrollment. Mohon tunggu atau coba beberapa saat lagi."
                            })
                        else:
                            device_manager.start_enrollment(license_key)
                            success = await device_manager.send_command(license_key, msg)
                            if not success:
                                device_manager.clear_enrollment(license_key)
                                await websocket.send_json({
                                    "event": "error",
                                    "error": "Device not connected"
                                })
                    else:
                        # Forward other commands to device
                        success = await device_manager.send_command(license_key, msg)
                        if not success:
                            await websocket.send_json({
                                "event": "error",
                                "error": "Device not connected"
                            })
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        device_manager.remove_watcher(license_key, websocket)


# HTTP endpoints for device status
@router.get("/devices/online")
async def get_online_devices():
    """Get list of currently connected devices."""
    connected = device_manager.get_all_connected()
    return {
        "success": True,
        "data": {
            "count": len(connected),
            "devices": [
                {
                    "license_key": lk,
                    "info": device_manager.get_device_info(lk)
                }
                for lk in connected
            ]
        }
    }


@router.post("/devices/{license_key}/command")
async def send_device_command(license_key: str, command: dict):
    """Send command to a connected device."""
    if not device_manager.is_connected(license_key):
        return {"success": False, "error": "Device not connected"}
    
    success = await device_manager.send_command(license_key, command)
    return {"success": success}


@router.post("/devices/{license_key}/clear-enrollment-lock")
async def clear_enrollment_lock(license_key: str):
    """Force-clear a stuck enrollment lock on a device (admin use)."""
    was_locked = device_manager.is_enrolling(license_key)
    device_manager.clear_enrollment(license_key)
    return {"success": True, "was_locked": was_locked}
