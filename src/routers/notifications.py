from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_user_payload
from src.models.notifications import NotificationUpdateRequest
from src.models.response import APIResponse
from src.schemas.tables.notifications import Notification

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    responses={404: {"error": "Not found"}}
    # ,
    # dependencies=[Depends(require_owner)]
)


@router.post("/mark_as_read")
def mark_as_read(
        payload: NotificationUpdateRequest,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user_payload)
):
    """"""
    try:
        if payload.mark_all_as_read:
            db.query(Notification).update({Notification.read: True})
        else:
            if payload.id:
                db.query(Notification).filter(Notification.id.in_(payload.id)).update(
                    {Notification.read: True}, synchronize_session=False
                )
        db.commit()
        return APIResponse(
            status_code=200,
            success=True,
            message=f"Notifications updated",
            data=None
        ).model_dump()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")


@router.get("/unread")
def get_unread_notifications(db: Session = Depends(get_db), current_user=Depends(get_current_user_payload)):
    unread = db.query(Notification).filter_by(read=False).all()
    return APIResponse(
        status_code=200,
        success=True,
        message=f"successfully fetched unread notifications",
        data=unread
    ).model_dump()
