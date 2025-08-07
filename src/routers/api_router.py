from fastapi import APIRouter

from . import patients, users, auth

router = APIRouter(prefix="/api", responses={404: {"error": "Not found"}}, )

# List of routers
routers = [patients.router, users.router, auth.router]

# Include all routers
for r in routers:
    router.include_router(r)
