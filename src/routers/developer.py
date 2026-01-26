from fastapi import APIRouter, Depends
from src.dependencies import get_current_doctor_id, require_owner
from src.database import get_db
from sqlalchemy.orm import Session
from src.schemas.tables.users import User
from src.models.response import APIResponse
from src.models.developers import DevelopersTabOut, UserOut

router = APIRouter(
    prefix="/developers",
    tags=["developers"],
    responses={404: {"error": "Not found"}},
    dependencies=[Depends(require_owner)]
)


@router.get("/get_all_users_list")
def get_all_users_list(db: Session = Depends(get_db),):
    """
    Used to get the client details in below format:

    Return fields would be(Client Name, Brand Name, Subscription Plan,Ends On,	Active/Inactive,Action)
    """
    query = db.query(User).all()
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Successfully fetched users lists.",
        data=[UserOut.from_row(p) for p in query]
    ).model_dump()

