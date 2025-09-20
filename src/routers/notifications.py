from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.models.notifications import NotificationUpdateRequest, NotificationOut
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
        doctor_id: UUID = Depends(get_current_doctor_id)
):
    """"""
    try:
        if payload.mark_all_as_read:
            db.query(Notification).filter_by(doctor_id=doctor_id).update({Notification.read: True})
        else:
            if payload.id:
                db.query(Notification).filter(Notification.doctor_id == doctor_id,
                                              Notification.id.in_(payload.id)).update(
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


@router.get("")
def get_notifications(page: int = Query(1, ge=1),
                      page_size: int = Query(20, ge=1),
                      status: Optional[str] = Query(None),
                      startDate: str = Query(None, description="Filter by start date in YYYY-MM-DD format"),
                      endDate: str = Query(None, description="Filter by end date in YYYY-MM-DD format"),
                      db: Session = Depends(get_db),
                      doctor_id: UUID = Depends(get_current_doctor_id),
                      ):
    """Fetch notifications, with optional filtering by type and date range."""
    query = db.query(Notification).filter_by(doctor_id=doctor_id)

    try:
        start_dt = datetime.fromisoformat(startDate)
        end_dt = datetime.fromisoformat(endDate)
        end_dt = end_dt.replace(hour=23, minute=59, second=59)
        query = query.filter(Notification.created_at.between(start_dt, end_dt))
    except Exception as ex:
        return APIResponse(
            status_code=200,
            success=True,
            message=f"Invalid date format. Please use YYYY-MM-DD, {str(ex)}",
            data=None
        ).model_dump()

    if status is None:
        msg = "all"
        query = query
    elif status.lower() == "read":
        msg = "read"
        query = query.filter_by(read=1)
    elif status.lower() == "unread":
        msg = "unread"
        query = query.filter_by(read=0)
    else:  # if status.lower() in [None, ""]:
        msg = "all"

    offset = (page - 1) * page_size
    results = query.order_by(desc(Notification.created_at)).offset(offset).limit(page_size).all()
    # import pdb;pdb.set_trace()
    #
    # print(NotificationOut.model_validate(results))

    return APIResponse(
        status_code=200,
        success=True,
        message=f"successfully fetched {msg} notifications",
        data=[NotificationOut.model_validate(row) for row in results]
    ).model_dump()
