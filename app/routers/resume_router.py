from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
import tempfile, shutil

from app.db.database import SessionLocal
from app.utils.file_utils import extract_text
from app.llm.extract_sections import extract_resume_sections
from app.services.resume_service import save_resume
from app.db import models
from fastapi import APIRouter, UploadFile, File, Depends, Form

router = APIRouter(prefix="/resume", tags=["Resume"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload/")
async def upload_resume(user_id: str = Form(...),
    phone: str = Form(...),
    full_name: str = Form(...),
    email: str = Form(...),
    linkedin: str = Form(""),
    github: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)):
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    # Extract text from file
    raw_text = extract_text(tmp_path, file.filename)

    # Extract sections with LLM
    sections = extract_resume_sections(raw_text)

    # Save to DB
    resume_id = save_resume(
    db=db,
    user_id=user_id,
    filename=file.filename,
    raw_text=raw_text,
    sections=sections,
    phone=phone,
    full_name=full_name,
    email=email,
    linkedin=linkedin,
    github=github,
)

    return {
        "message": "Resume uploaded and parsed successfully.",
        "resume_id": resume_id,
        "sections": sections
    }


# ✅ FIXED — Delete resume endpoint
@router.delete("/delete")
def delete_resume(user_id: str, db: Session = Depends(get_db)):

    # Delete generated resumes
    db.query(models.GeneratedResume).filter(
        models.GeneratedResume.job_id.in_(
            db.query(models.Job.id).filter_by(user_id=user_id)
        )
    ).delete()

    # Delete resume sections
    db.query(models.ResumeSections).filter(
        models.ResumeSections.resume_id.in_(
            db.query(models.Resume.id).filter_by(user_id=user_id)
        )
    ).delete()

    # Delete resume
    db.query(models.Resume).filter_by(user_id=user_id).delete()

    db.commit()
    return {"status": "resume deleted"}