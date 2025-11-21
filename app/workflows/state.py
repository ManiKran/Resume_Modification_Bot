from pydantic import BaseModel
from typing import Dict, List, Optional, Any

class ResumeOptimizerState(BaseModel):
    resume_sections: Dict[str, Any]  # current working resume sections

    # Personal info added by user
    phone: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None

    # Education stays as a list of dicts
    original_education: List[Dict[str, Any]]

    # mapping of positions/company/dates (can stay dict)
    original_experience_positions: Dict[str, Any]

    job_description: str

    # ATS results
    ats_score: Optional[int] = None
    analysis: Optional[Dict[str, Any]] = None

    iteration_count: int = 0
    passed: bool = False
    final_docx_path: Optional[str] = None