from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import os
import uuid
from fastapi import APIRouter

router = APIRouter(
    prefix="/upload_images", tags=["upload_images"], responses={404: {"error": "Not found"}}
    # , dependencies=[Depends(require_owner)]
)
# app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-profile-image/")
async def upload_profile_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save the file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    return {"filename": unique_filename, "url": f"/profile-images/{unique_filename}"}


@router.get("/profile-images/{filename}")
async def get_profile_image(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Image not found")
