from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import require_owner
from src.models.developers import DevelopersTabOut, UserUpdate
from src.models.response import APIResponse
from src.models.subscription import SubscriptionOutWithPlan
from src.schemas.tables.subscription import Subscription
from src.schemas.tables.users import User

router = APIRouter(
    prefix="/developers",
    tags=["developers"],
    responses={404: {"error": "Not found"}},
    dependencies=[Depends(require_owner)]
)


@router.get("/get_all_users_list")
def get_all_users_list(db: Session = Depends(get_db)):
    """
    Used to get the client details in below format:

    Return fields would be(Client Name, Brand Name, Subscription Plan,Ends On,	Active/Inactive,Action)
    """
    # user_query = db.query(User).all()
    # subscription_query = db.query(Subscription).filter(Subscription.user_id == user_id).first()

    results = (
        db.query(User, Subscription)
        .join(Subscription, User.id == Subscription.user_id)
        .filter(Subscription.is_active == True)
        .all()
    )
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Successfully fetched users lists.",
        data=[DevelopersTabOut.from_row(db, user, subscription) for user, subscription in results]
    ).model_dump()


@router.get("/{doctor_id}", response_model=APIResponse)
def get_subscriptions_details_particular_doctor(doctor_id: str, db: Session = Depends(get_db)):
    all_subscription_details = db.query(Subscription).filter(
        Subscription.user_id == doctor_id).all()
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Successfully fetched the subscription data!",
        data=[SubscriptionOutWithPlan.from_orm(row) for row in all_subscription_details],
    ).model_dump()


@router.put("/users/{user_id}")
def update_user_details(user_id: str, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user fields if provided
    if payload.firstName is not None:
        user.firstName = payload.firstName
    if payload.lastName is not None:
        user.lastName = payload.firstName
    if payload.email is not None:
        user.email = payload.email

    # Update subscription if provided
    if payload.subscription:
        subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
        # if not subscription:
        #     # If no subscription exists, create one
        #     subscription = Subscription(user_id=user_id)
        #     db.add(subscription)

        # if payload.subscription.plan_name is not None:
        #     subscription.plan.plan_name = payload.subscription.plan_name
        if payload.subscription.start_date is not None:
            subscription.start_date = payload.subscription.start_date
        if payload.subscription.end_date is not None:
            subscription.end_date = payload.subscription.end_date
        if payload.subscription.is_active is not None:
            subscription.is_active = payload.subscription.is_active

    db.commit()
    db.refresh(user)

    return APIResponse(
        status_code=200,
        success=True,
        message=f"User details updated successfully!",
        data=None,
    ).model_dump()
