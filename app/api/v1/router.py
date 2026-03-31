from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    merchants,
    outlets,
    devices,
    customers,
    wallets,
    transactions,
    enrollment,
    biometric,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(merchants.router, prefix="/merchants", tags=["Merchants"])
api_router.include_router(outlets.router, prefix="/outlets", tags=["Outlets"])
api_router.include_router(devices.router, prefix="/devices", tags=["Devices"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(wallets.router, prefix="/wallets", tags=["Wallets"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(enrollment.router, prefix="/enrollment", tags=["Enrollment"])
api_router.include_router(biometric.router, prefix="/biometric", tags=["Biometric (Device)"])
