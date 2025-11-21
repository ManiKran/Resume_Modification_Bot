from sqlalchemy.orm import Session
from app.db import models

def save_job(db: Session, user_id: str, jd_text: str):
    job = models.Job(
        user_id=user_id,
        jd_text=jd_text
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job.id


def get_user_resume_sections(db: Session, user_id: str):
    resume = db.query(models.Resume).filter_by(user_id=user_id).order_by(models.Resume.created_at.desc()).first()

    if not resume:
        return None

    sections = db.query(models.ResumeSections).filter_by(resume_id=resume.id).first()

    if not sections:
        return None

    return {
        "summary": sections.summary,
        "experience": sections.experience,
        "education": sections.education,
        "skills": sections.skills
    }