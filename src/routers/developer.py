from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import require_owner
from src.models.developers import (
    DevelopersTabOut,
    DeveloperUserUpdate,
    UserWithAllSubscription,
)
from src.models.response import APIResponse
from src.schemas.tables.interested_users import InterestedUser
from src.schemas.tables.subscription import Subscription
from src.schemas.tables.users import User
from src.schemas.tables.plans import Plan

router = APIRouter(
    prefix="/developers",
    tags=["developers"],
    responses={404: {"error": "Not found"}},
    dependencies=[Depends(require_owner)],
)


@router.get("/get_all_users_list")
def get_all_users_list(db: Session = Depends(get_db)):
    """
    Used to get the client details in below format:

    Return fields would be(Client Name, Brand Name, Subscription Plan,Ends On,	Active/Inactive,Action)
    """
    # user_query = db.query(User).all()
    # subscription_query = db.query(Subscription).filter(Subscription.user_id == user_id).first()

    # results = (
    #     db.query(User, Subscription)
    #     .join(Subscription, User.id == Subscription.user_id)
    #     .filter(Subscription.is_active == True)
    #     .all()
    # )
    latest_sub = (
        db.query(
            Subscription.user_id,
            func.max(Subscription.end_date).label("latest_end_date"),
        )
        .group_by(Subscription.user_id)
        .subquery()
    )
    result = (
        db.query(User, Subscription)
        .join(latest_sub, User.id == latest_sub.c.user_id)
        .join(
            Subscription,
            (Subscription.user_id == latest_sub.c.user_id)
            & (Subscription.end_date == latest_sub.c.latest_end_date),
        )
        .all()
    )

    # results = db.query(User).all()
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Successfully fetched users lists.",
        data=[
            DevelopersTabOut.from_row(db, user, subscription)
            for user, subscription in result
        ],
    ).model_dump()


@router.get("/interested_users")
def get_interested_users_list(db: Session = Depends(get_db)):
    interested_users = db.query(InterestedUser).all()
    if not interested_users:
        raise HTTPException(status_code=404, detail="No interested user found")
    interested_users_list = []
    for row in interested_users:
        # db_user = db.query(User).filter_by(id=row.doctor_id).first()
        # if not db_user:
        #     raise HTTPException(status_code=404, detail="User not found")
        # plan_details = db.query(Plan).filter_by(id=row.plan_id).first()
        # if not plan_details:
        #     raise HTTPException(status_code=404, detail="Plan details not found")
        interested_users_list.append(
            {
                "user_firstName": row.user.firstName,
                "user_lastName": row.user.lastName,
                "user_mobile": row.user.mobile,
                "plan_name": row.plan.name,
                "plan_price": row.plan.price,
                "created_at": row.created_at,
            }
        )
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Successfully fetched interested users lists.",
        data=interested_users_list,
    ).model_dump()


@router.get("/{doctor_id}", response_model=APIResponse)
def get_subscriptions_details_particular_doctor(
    doctor_id: str, db: Session = Depends(get_db)
):
    # all_subscription_details = db.query(Subscription).filter(
    #     Subscription.user_id == doctor_id).all()
    results = db.query(User).filter(User.id == doctor_id).all()
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Successfully fetched the subscription data!",
        data=[UserWithAllSubscription.from_row(db, row) for row in results],
    ).model_dump()


@router.put("/users")
def update_user_details(payload: DeveloperUserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user fields if provided
    if payload.firstName is not None:
        user.firstName = payload.firstName
    if payload.lastName is not None:
        user.lastName = payload.lastName
    if payload.email is not None:
        user.email = payload.email
    if payload.country is not None:
        user.country = payload.country
    if payload.mobile is not None:
        user.mobile = payload.mobile
    db.add(user)

    # Update subscription if provided
    # if payload.subscription:
    subscription = (
        db.query(Subscription)
        .filter(Subscription.user_id == payload.user_id)
        .order_by(Subscription.created_at.desc())
        .first()
    )
    # if not subscription:
    #     # If no subscription exists, create one
    #     subscription = Subscription(user_id=user_id)
    #     db.add(subscription)
    if subscription:
        plans = (
            db.query(Plan).filter(Plan.name == payload.subscription.plan_name).first()
        )
        if plans:
            subscription.plan = plans
        if payload.subscription.start_date is not None:
            subscription.start_date = payload.subscription.start_date
        if payload.subscription.end_date is not None:
            subscription.end_date = payload.subscription.end_date
        if payload.subscription.is_active is not None:
            subscription.is_active = payload.subscription.is_active
    else:
        raise HTTPException(status_code=404, detail="Subscription not found")
    db.add(subscription)
    db.commit()
    db.refresh(user)
    db.refresh(subscription)

    return APIResponse(
        status_code=200,
        success=True,
        message=f"User details updated successfully!",
        data=None,
    ).model_dump()
