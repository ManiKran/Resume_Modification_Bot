from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .database import Base


def generate_uuid():
    return str(uuid.uuid4())


# -------------------------------------------------------
# USERS
# -------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# -------------------------------------------------------
# RESUME (uploads + raw text + contact info)
# -------------------------------------------------------

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(String, index=True)
    filename = Column(String)
    raw_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # New user contact info fields
    phone = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    linkedin = Column(String, nullable=True)
    github = Column(String, nullable=True)

    sections = relationship("ResumeSections", backref="resume", uselist=False, cascade="all, delete-orphan")


# -------------------------------------------------------
# PARSED RESUME SECTIONS (summary, experience, education, skills)
# -------------------------------------------------------

class ResumeSections(Base):
    __tablename__ = "resume_sections"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    resume_id = Column(UUID(as_uuid=False), ForeignKey("resumes.id", ondelete="CASCADE"))

    summary = Column(JSONB)
    experience = Column(JSONB)
    education = Column(JSONB)
    skills = Column(JSONB)

    parsed_at = Column(DateTime, default=datetime.utcnow)


# -------------------------------------------------------
# JOB (job descriptions submitted by the user)
# -------------------------------------------------------

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(String, index=True)
    jd_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    generated_resumes = relationship("GeneratedResume", backref="job", cascade="all, delete-orphan")


# -------------------------------------------------------
# GENERATED RESUMES (ATS output + generated DOCX + analysis)
# -------------------------------------------------------

class GeneratedResume(Base):
    __tablename__ = "generated_resumes"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    job_id = Column(UUID(as_uuid=False), ForeignKey("jobs.id", ondelete="CASCADE"))

    resume_sections_json = Column(JSONB)  # full tailored resume
    ats_score = Column(Integer)
    analysis_json = Column(JSONB)
    iteration_count = Column(Integer)
    file_url = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)