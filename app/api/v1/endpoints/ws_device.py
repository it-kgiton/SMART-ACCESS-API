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
from typing import Dict, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from loguru import logger

from app.core.database import AsyncSessionLocal
from app.models.device import Device, DeviceStatus


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
        logger.info(f"[WS] Device disconnected: {license_key}")
        
        # Notify dashboard watchers
        asyncio.create_task(self._notify_watchers(license_key, {
            "event": "device_offline",
            "license_key": license_key
        }))
    
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
            # Receive message from device
            data = await websocket.receive_text()
            
            try:
                msg = json.loads(data)
                event = msg.get("event")
                
                if event == "connected":
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
                    # Forward enrollment events to watchers
                    await device_manager.forward_to_watchers(license_key, msg)
                    
                    if event == "enroll_ok":
                        logger.info(f"[WS] Enroll OK: {license_key} customer={msg.get('customer_id')}")
                
                elif event in ("verify_start", "verify_scan", "verify_processing",
                               "verify_request", "verify_batch_ok", "verify_ok", 
                               "verify_fail"):
                    # Forward verify events to watchers
                    await device_manager.forward_to_watchers(license_key, msg)
                    
                    if event == "verify_ok":
                        logger.info(f"[WS] Verify OK: {license_key} customer={msg.get('customer_id')} score={msg.get('confidence')}")
                    elif event == "verify_request":
                        # Device requesting templates for matching
                        logger.info(f"[WS] Verify request from {license_key}")
                
                elif event == "pong":
                    pass  # Response to ping
                
                elif event == "cancelled":
                    await device_manager.forward_to_watchers(license_key, msg)
                
                else:
                    logger.debug(f"[WS] Unknown event from {license_key}: {event}")
                    await device_manager.forward_to_watchers(license_key, msg)
                    
            except json.JSONDecodeError:
                logger.warning(f"[WS] Invalid JSON from {license_key}: {data[:100]}")
                
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
                    # Forward command to device
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
