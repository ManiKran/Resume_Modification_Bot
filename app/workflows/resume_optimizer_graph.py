from langgraph.graph import StateGraph
from .state import ResumeOptimizerState
from app.services.llm_optimizer import tailor_resume
from app.services.llm_ats import ats_score
from app.services.llm_improver import improve_resume
from app.services.docx_generator import generate_final_docx
import os
import uuid


# -----------------------------------------
# CONFIG
# -----------------------------------------
ATS_THRESHOLD = 85
MAX_LOOPS = 1


# -----------------------------------------
# NODES
# -----------------------------------------

def node_tailor(state: ResumeOptimizerState):
    """
    First LLM pass:
    - Tailors SUMMARY, EXPERIENCE bullets, SKILLS
    - MUST NOT modify EDUCATION
    """
    tailored = tailor_resume(
        state.resume_sections,
        state.job_description,
        state.original_experience_positions
    )

    state.resume_sections["summary"] = tailored["summary"]
    state.resume_sections["experience"] = tailored["experience"]
    state.resume_sections["skills"] = tailored["skills"]

    # Preserve education exactly (list of objects)
    state.resume_sections["education"] = state.original_education

    return state


def node_ats(state: ResumeOptimizerState):
    """
    ATS Scoring Step
    """
    result = ats_score(state.resume_sections, state.job_description)
    state.ats_score = result["score"]
    state.analysis = result["analysis"]
    return state


def check_score(state: ResumeOptimizerState):
    """
    Decide the next node:
    - PASS → GENERATE
    - STOP → GENERATE (max attempts reached)
    - IMPROVE → run improve node again
    """
    if state.ats_score >= ATS_THRESHOLD:
        return "PASS"
    if state.iteration_count >= MAX_LOOPS:
        return "STOP"
    return "IMPROVE"


def node_improve(state: ResumeOptimizerState):
    """
    Improvement loop:
    - Modifies summary, experience bullets, skills
    - Education stays unchanged
    """
    improved = improve_resume(
        state.resume_sections,
        state.analysis,
        state.job_description,
        state.original_experience_positions
    )

    state.resume_sections["summary"] = improved["summary"]
    state.resume_sections["experience"] = improved["experience"]
    state.resume_sections["skills"] = improved["skills"]

    # preserve education
    state.resume_sections["education"] = state.original_education

    state.iteration_count += 1
    return state


def node_generate(state: ResumeOptimizerState):
    """
    Final step.
    Generates DOCX using user info + tailored sections.
    """
    import os
    import uuid
    from app.services.docx_generator import generate_final_docx

    os.makedirs("generated", exist_ok=True)

    unique_filename = f"final_resume_{uuid.uuid4()}.docx"
    output_path = f"generated/{unique_filename}"

    # Build user info block for DOCX header
    user_info = {
        "full_name": state.full_name,
        "phone":state.phone,
        "email": state.email,
        "linkedin": state.linkedin,
        "github": state.github,
    }

    generate_final_docx(
        sections=state.resume_sections,
        user_info=user_info,
        output_path=output_path,
    )

    state.final_docx_path = unique_filename
    state.passed = True
    return state


# -----------------------------------------
# BUILD THE GRAPH
# -----------------------------------------

builder = StateGraph(ResumeOptimizerState)

builder.add_node("TAILOR", node_tailor)
builder.add_node("ATS", node_ats)
builder.add_node("IMPROVE", node_improve)
builder.add_node("GENERATE", node_generate)

builder.set_entry_point("TAILOR")

builder.add_edge("TAILOR", "ATS")

builder.add_conditional_edges(
    "ATS",
    check_score,
    {
        "PASS": "GENERATE",
        "STOP": "GENERATE",
        "IMPROVE": "IMPROVE",
    }
)

builder.add_edge("IMPROVE", "ATS")

resume_optimizer_graph = builder.compile()