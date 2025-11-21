from sqlalchemy.orm import Session
from app.db import models

def save_resume(
    db: Session,
    user_id: str,
    filename: str,
    raw_text: str,
    sections: dict,
    phone: str,
    full_name: str,
    email: str,
    linkedin: str,
    github: str,
):
    # 1. Save Resume
    resume = models.Resume(
        user_id=user_id,
        filename=filename,
        raw_text=raw_text,
        phone = phone,
        full_name=full_name,
        email=email,
        linkedin=linkedin,
        github=github,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    # 2. Save Sections
    resume_sections = models.ResumeSections(
        resume_id=resume.id,
        summary=sections.get("summary"),
        experience=sections.get("experience"),
        education=sections.get("education"),
        skills=sections.get("skills")
    )
    db.add(resume_sections)
    db.commit()

    return resume.id