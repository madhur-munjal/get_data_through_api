from fastapi import APIRouter

from . import patients, users, auth, staff, appointments, visits, settings, billing, dashboard, notifications, subscription, upload_images, plans

router = APIRouter(
    # prefix="/api",
    responses={404: {"error": "Not found"}}
    # ,
    # dependencies=[Depends(require_owner)]
)

# List of routers
routers = [
    patients.router,
    users.router,
    auth.router,
    staff.router,
    appointments.router,
    visits.router,
    settings.router,
    billing.router,
    dashboard.router,
    notifications.router,
    subscription.router,
    # upload_images.router
    plans.router,

]

# Include all routers
for r in routers:
    router.include_router(r, tags=r.tags)  #  prefix=r.prefix
