from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.models.response import APIResponse
from src.models.users import UserOut
from src.models.plans import PlanOut
from src.models.subscription import SubscriptionCreate, SubscriptionRead  # Pydantic models
from src.schemas.tables.subscription import Subscription  # SQLAlchemy model
from src.schemas.tables.users import User
from src.schemas.tables.plans import Plan

router = APIRouter(
    prefix="/subscriptions", tags=["Subscriptions"], responses={404: {"error": "Not found"}}
    # , dependencies=[Depends(require_owner)]
)


# 📥 Create a new subscription
@router.post("/", response_model=APIResponse[SubscriptionRead])
def create_subscription(subscription: SubscriptionCreate, db: Session = Depends(get_db),
                        doctor_id: UUID = Depends(get_current_doctor_id)):
    input_data = subscription.dict()
    input_data["user_id"] = str(doctor_id)
    new_sub = Subscription(**input_data)
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Subscription has been created successfully!",
        data=SubscriptionRead.model_validate(new_sub),
    ).model_dump()


@router.post("/send_subscription_details_on_mail/{plan_id}", response_model=APIResponse[SubscriptionRead])
def send_subscription_details_on_mail(plan_id, db: Session = Depends(get_db),
                        doctor_id: UUID = Depends(get_current_doctor_id)):
    db_user = (
        db.query(User)
        .filter_by(id=doctor_id)
        .first()
    )
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    print("user details")
    print([UserOut.model_validate(db_user)])
    print("*************")

    plan_details = (
        db.query(Plan)
        .filter_by(id=plan_id)
        .first()
    )
    if not plan_details:
        raise HTTPException(status_code=404, detail="User not found")
    print("plan details")
    print([PlanOut.model_validate(plan_details)])
    print("*************")

    from src.utility import send_msg_on_email as send_email
    subject = "User Interested in Subscription – Action Required"
    body = f"""
    Dear team,

    User Subscription Interest Logged

    User Details:
    - Name: {db_user.firstName + " " + db_user.lastName}
    - User ID: {db_user.id}
    - Email: {db_user.email}
    - Mobile: {db_user.mobile}
    - Time: {datetime.now()}
    - Country: {db_user.country}
    - Username: {db_user.username}
    - Role: {db_user.role}


    Subscription Details:
    TODO
     Type: [e.g., Premium, Annual, Trial]
    - Notes: [Any additional context or user comments]
    
    Next Steps:
    - [ ] Send follow-up email
    - [ ] Assign to sales/support team
    - [ ] Add to CRM or lead tracker
    
    Logged by: [Your Name or System ID]
    Your staff account details have been updated. Here are your updated details:


    If you did not request this change, please contact the administrator immediately.

    Best regards,
    SmartHealApp Management Team
    """
    send_email(to_email=os.getenv("from_email_id"), message=body, Subject=subject)

    return APIResponse(
        status_code=200,
        success=True,
        message=f"Smart-Heal management team will get back to you shortly!",
        # data=None,
    ).model_dump()



# # 📄 Get all subscriptions
# @router.get("/", response_model=list[SubscriptionRead])
# def list_subscriptions(db: Session = Depends(get_db), doctor_id: UUID = Depends(get_current_doctor_id)):
#     query = db.query(Subscription).all()
#     return APIResponse(
#         status_code=200,
#         success=True,
#         message=f"New staff account has been created successfully!",
#         data=query,
#     ).model_dump()
#     # return
#
#
# # 🔍 Get subscription by ID
# @router.get("/{subscription_id}", response_model=SubscriptionRead)
# def get_subscription(subscription_id: UUID, db: Session = Depends(get_db), doctor_id: UUID = Depends(get_current_doctor_id)):
#     sub = db.query(Subscription).filter(Subscription.id == str(subscription_id)).first()
#     if not sub:
#         raise HTTPException(status_code=404, detail="Subscription not found")
#     return APIResponse(
#         status_code=200,
#         success=True,
#         message=f"New staff account has been created successfully!",
#         data=sub,
#     ).model_dump()
#
#
# # 🔄 Update subscription (e.g., change plan or dates)
# @router.put("/{subscription_id}", response_model=SubscriptionRead)
# def update_subscription(subscription_id: UUID, updated: SubscriptionCreate, db: Session = Depends(get_db), doctor_id: UUID = Depends(get_current_doctor_id)):
#     sub = db.query(Subscription).filter(Subscription.id == str(subscription_id)).first()
#     if not sub:
#         raise HTTPException(status_code=404, detail="Subscription not found")
#     for key, value in updated.dict(exclude_unset=True).items():
#         setattr(sub, key, value)
#     db.commit()
#     db.refresh(sub)
#     return APIResponse(
#         status_code=200,
#         success=True,
#         message=f"New staff account has been created successfully!",
#         data=sub,
#     ).model_dump()
#
#
# # ❌ Deactivate subscription
# @router.patch("/{subscription_id}/deactivate", response_model=SubscriptionRead)
# def deactivate_subscription(subscription_id: UUID, db: Session = Depends(get_db), doctor_id: UUID = Depends(get_current_doctor_id)):
#     sub = db.query(Subscription).filter(Subscription.id == str(subscription_id)).first()
#     if not sub:
#         raise HTTPException(status_code=404, detail="Subscription not found")
#     sub.is_active = False
#     db.commit()
#     db.refresh(sub)
#     return APIResponse(
#         status_code=200,
#         success=True,
#         message=f"New staff account has been created successfully!",
#         data=sub,
#     ).model_dump()
