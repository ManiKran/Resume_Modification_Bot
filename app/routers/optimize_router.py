from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.services.job_service import get_user_resume_sections
from app.workflows.resume_optimizer_graph import resume_optimizer_graph, ResumeOptimizerState
from app.db.models import Resume   # ← IMPORTANT: import Resume model

router = APIRouter(prefix="/optimize", tags=["Optimize"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def optimize_resume(
    user_id: str,
    job_description: str,
    request: Request,
    db: Session = Depends(get_db),
):

    # Fetch parsed resume sections from DB
    sections = get_user_resume_sections(db, user_id)
    if not sections:
        return {"error": "User has no saved resume."}

    # Fetch user personal info from Resume table
    resume_record = db.query(Resume).filter_by(user_id=user_id).first()
    if not resume_record:
        return {"error": "User resume record missing."}

    # Experience locks (reserved for future use)
    experience_locks = {}

    # Structured education stays AS-IS (list of objects)
    original_education_list = sections["education"]

    # Build initial LangGraph state
    state = ResumeOptimizerState(
        resume_sections=sections,
        original_education=original_education_list,
        original_experience_positions=experience_locks,
        job_description=job_description,

        # NEW FIELDS
        phone=resume_record.phone,
        full_name=resume_record.full_name,
        email=resume_record.email,
        linkedin=resume_record.linkedin,
        github=resume_record.github,
    )

    # Run the optimization workflow
    final_state = resume_optimizer_graph.invoke(state)

    # Build full URL for DOCX file
    base_url = str(request.base_url)
    full_url = f"{base_url}generated/{final_state['final_docx_path']}"

    return {
        "ats_score": final_state["ats_score"],
        "resume": final_state["resume_sections"],
        "analysis": final_state["analysis"],
        "iterations": final_state["iteration_count"],
        "file_url": full_url,
        "file_url_relative": f"/generated/{final_state['final_docx_path']}"
    }