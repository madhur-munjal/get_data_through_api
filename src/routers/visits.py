from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_user
from src.models.response import APIResponse
from src.models.visits import VisitOut

# from src.schemas.tables.visits import Visit

router = APIRouter(
    prefix="/visits", tags=["visits"], responses={404: {"error": "Not found"}}
)
# APIResponse(
#         status_code=404,
#         success=False,
#         message="Not found",
#         data=None,
#     ).model_dump())


# @router.get("/visits_list", response_model=APIResponse)
# def get_visits(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
#     """Fetch all users."""
#     visits = db.query(Visit).all()
#     user_dtos = [VisitOut.model_validate(visit) for visit in visits]
#     return APIResponse(
#         status_code=200,
#         success=True,
#         message="successfully fetched visits",
#         data=user_dtos,
#     ).model_dump()
