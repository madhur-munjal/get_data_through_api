from fastapi import APIRouter

from . import medical

router = APIRouter(prefix="/api", responses={404: {"error": "Not found"}}, )

# List of routers
routers = [medical.router]

# Include all routers
for r in routers:
    router.include_router(r)
