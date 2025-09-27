from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.plans import PlanCreate, PlanOut
from src.models.response import APIResponse
from src.schemas.tables.plans import Plan

router = APIRouter(prefix="/plans", tags=["Plans"])


@router.post("", response_model=APIResponse[PlanOut])
def create_plan(plan: PlanCreate, db: Session = Depends(get_db)):
    existing = db.query(Plan).filter_by(name=plan.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Plan already exists")
    new_plan = Plan(**plan.dict())
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Plans has been created successfully!",
        data=PlanOut.model_validate(new_plan),
    ).model_dump()


@router.get("", response_model=APIResponse)
def list_plans(db: Session = Depends(get_db)):
    all_plan_details = db.query(Plan).all()
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Successfully fetched list of plans!",
        data=[PlanOut.model_validate(row) for row in all_plan_details],
    ).model_dump()


@router.get("/{plan_id}", response_model=APIResponse[PlanOut])
def get_plan(plan_id: str, db: Session = Depends(get_db)):
    plan = db.query(Plan).get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Successfully fetched plan details!",
        data=PlanOut.model_validate(plan),
    ).model_dump()
