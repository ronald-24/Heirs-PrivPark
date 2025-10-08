from fastapi import APIRouter

from app.api.routes_auth import router as auth_router
from app.api.routes_users import router as users_router
from app.api.routes_parking import router as parking_router
from app.api.routes_booking import router as bookings_router
from app.api.routes_payments import router as payments_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(parking_router)
api_router.include_router(bookings_router)
api_router.include_router(payments_router)
