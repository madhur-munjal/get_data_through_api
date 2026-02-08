import os
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.constants import total_appointments_basic_plan, total_appointments_professional_plan
from src.database import get_db
from src.dependencies import get_current_doctor_id, require_owner
from src.models.plans import PlanDetailsOnMail
from src.models.response import APIResponse
from src.models.subscription import (
    SubscriptionCreate,
    SubscriptionRead,
)  # Pydantic models
from src.models.subscription import SubscriptionOutWithPlan
from src.schemas.tables.interested_users import InterestedUser
from src.schemas.tables.plans import Plan
from src.schemas.tables.subscription import Subscription  # SQLAlchemy model
from src.schemas.tables.users import User
from src.utility import update_subscription_data, send_msg_on_email, save_data_to_db, get_appointments_left_by_doctor

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"],
    responses={404: {"error": "Not found"}},
    # , dependencies=[Depends(require_owner)]
)


# 📥 Create a new subscription
@router.post("", response_model=APIResponse[SubscriptionRead])
def create_subscription(
        subscription: SubscriptionCreate,
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
        dependencies=Depends(require_owner),
):
    input_data = subscription.dict()
    doctor_id = str(doctor_id)
    if subscription.user_id is None:
        input_data["user_id"] = doctor_id
    else:
        input_data["user_id"] = str(subscription.user_id)
    appointments_left = get_appointments_left_by_doctor(db, doctor_id)
    # TODO: set appointment credits to zero for old subscription on new subscription creation
    plan_details = db.query(Plan).filter_by(id=subscription.plan_id).first()
    if plan_details.name == "Basic":
        input_data["appointment_credits"] = total_appointments_basic_plan + appointments_left
    elif plan_details.name == "Professional":
        input_data["appointment_credits"] = total_appointments_professional_plan + appointments_left
    else:
        input_data["appointment_credits"] = subscription.appointment_credits + appointments_left
    new_sub = Subscription(**input_data)
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    update_subscription_data()
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Subscription has been created successfully!",
        data=SubscriptionRead.model_validate(new_sub),
    ).model_dump()


@router.post(
    "/send_subscription_details_on_mail", response_model=APIResponse[SubscriptionRead]
)
def send_subscription_details_on_mail(
        plan_details: PlanDetailsOnMail,
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
):
    db_user = db.query(User).filter_by(id=doctor_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    plan_details = db.query(Plan).filter_by(id=plan_details.plan_id).first()
    if not plan_details:
        raise HTTPException(status_code=404, detail="Plan details not found")

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
    - Name: {plan_details.name}
    - Description: {plan_details.description}
    - Price: {plan_details.price}
    - Currency: {plan_details.currency}
    
    Next Steps:
    - [ ] Send follow-up email
    - [ ] Assign to sales/support team
    - [ ] Add to CRM or lead tracker
    
    Thank you,
    Best regards,
    SmartHealApp Management Team
    """
    interested_users_data = {'doctor_id': str(doctor_id), 'plan_id': plan_details.id}
    save_data_to_db(interested_users_data, InterestedUser, db)
    send_msg_on_email(
        to_email=os.getenv("from_email_id"), message=body, Subject=subject
    )
    # send_email(to_email=os.getenv("from_email_id"), message=body, Subject=subject)
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Thank you for showing interest on Smart Heal. Smart-Heal support team will get back to you shortly!",
        # data=None,
    ).model_dump()


# @router.post("/sync_subscriptions", response_model=APIResponse[SubscriptionRead])
# def update_subscription_data(db: Session = Depends(get_db),
#                              doctor_id: UUID = Depends(get_current_doctor_id)):
#     today = date.today()
#
#     # Step 1: Deactivate expired subscriptions
#     expired = db.query(Subscription).filter(Subscription.end_date < today, Subscription.is_active == True).all()
#     for sub in expired:
#         sub.is_active = False
#
#     # Step 2: For each doc_id, activate only the latest valid subscription
#     user_ids = db.query(Subscription.user_id).distinct().all()
#     for (user_id,) in user_ids:
#         latest = (
#             db.query(Subscription)
#             .filter(Subscription.user_id == user_id, Subscription.end_date >= today)
#             .order_by(Subscription.end_date.desc())
#             .first()
#         )
#         if latest:
#             latest.is_active = True
#
#         # Deactivate others for this doc_id
#         others = (
#             db.query(Subscription)
#             .filter(Subscription.user_id == user_id, Subscription.id != latest.id if latest else True)
#             .all()
#         )
#         for sub in others:
#             sub.is_active = False
#
#     db.commit()
#     return APIResponse(
#         status_code=200,
#         success=True,
#         message=f"Subscription data has been synced successfully!",
#         data=None,
#     ).model_dump()


@router.get("/get_subscription", response_model=APIResponse)
def get_subscription(
        db: Session = Depends(get_db), doctor_id: UUID = Depends(get_current_doctor_id)
):
    all_subscription_details = (
        db.query(Subscription).filter(Subscription.user_id == doctor_id).all()
    )
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Successfully fetched the subscription data!",
        data=[
            SubscriptionOutWithPlan.from_orm(row) for row in all_subscription_details
        ],
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
