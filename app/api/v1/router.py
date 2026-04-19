from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    organizations,
    merchants,
    products,
    parents,
    clients,
    devices,
    wallets,
    transactions,
    enrollment,
    biometric,
    tickets,
    notifications,
    approvals,
    dashboard,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(merchants.router, prefix="/merchants", tags=["Merchants"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(parents.router, prefix="/parents", tags=["Parents"])
api_router.include_router(clients.router, prefix="/clients", tags=["Clients"])
api_router.include_router(devices.router, prefix="/devices", tags=["Devices"])
api_router.include_router(wallets.router, prefix="/wallets", tags=["Wallets"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(enrollment.router, prefix="/enrollment", tags=["Enrollment"])
api_router.include_router(biometric.router, prefix="/biometric", tags=["Biometric (Device)"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["Tickets"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["Approvals"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
