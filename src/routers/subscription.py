from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.models.response import APIResponse
from src.models.subscription import SubscriptionCreate, SubscriptionRead  # Pydantic models
from src.schemas.tables.subscription import Subscription  # SQLAlchemy model

router = APIRouter(
    prefix="/subscriptions", tags=["Subscriptions"], responses={404: {"error": "Not found"}}
    # , dependencies=[Depends(require_owner)]
)


# 📥 Create a new subscription
@router.post("/", response_model=APIResponse[SubscriptionRead])
def create_subscription(subscription: SubscriptionCreate, db: Session = Depends(get_db),
                        doctor_id: UUID = Depends(get_current_doctor_id)):
    new_sub = Subscription(**subscription.dict())
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return APIResponse(
        status_code=200,
        success=True,
        message=f"New staff account has been created successfully!",
        data=SubscriptionRead.model_validate(new_sub),
    ).model_dump()


# 📄 Get all subscriptions
@router.get("/", response_model=list[SubscriptionRead])
def list_subscriptions(db: Session = Depends(get_db), doctor_id: UUID = Depends(get_current_doctor_id)):
    query = db.query(Subscription).all()
    return APIResponse(
        status_code=200,
        success=True,
        message=f"New staff account has been created successfully!",
        data=query,
    ).model_dump()
    # return


# 🔍 Get subscription by ID
@router.get("/{subscription_id}", response_model=SubscriptionRead)
def get_subscription(subscription_id: UUID, db: Session = Depends(get_db), doctor_id: UUID = Depends(get_current_doctor_id)):
    sub = db.query(Subscription).filter(Subscription.id == str(subscription_id)).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return APIResponse(
        status_code=200,
        success=True,
        message=f"New staff account has been created successfully!",
        data=sub,
    ).model_dump()


# 🔄 Update subscription (e.g., change plan or dates)
@router.put("/{subscription_id}", response_model=SubscriptionRead)
def update_subscription(subscription_id: UUID, updated: SubscriptionCreate, db: Session = Depends(get_db), doctor_id: UUID = Depends(get_current_doctor_id)):
    sub = db.query(Subscription).filter(Subscription.id == str(subscription_id)).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    for key, value in updated.dict(exclude_unset=True).items():
        setattr(sub, key, value)
    db.commit()
    db.refresh(sub)
    return APIResponse(
        status_code=200,
        success=True,
        message=f"New staff account has been created successfully!",
        data=sub,
    ).model_dump()


# ❌ Deactivate subscription
@router.patch("/{subscription_id}/deactivate", response_model=SubscriptionRead)
def deactivate_subscription(subscription_id: UUID, db: Session = Depends(get_db), doctor_id: UUID = Depends(get_current_doctor_id)):
    sub = db.query(Subscription).filter(Subscription.id == str(subscription_id)).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    sub.is_active = False
    db.commit()
    db.refresh(sub)
    return APIResponse(
        status_code=200,
        success=True,
        message=f"New staff account has been created successfully!",
        data=sub,
    ).model_dump()
