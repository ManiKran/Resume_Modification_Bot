import logging
from langgraph.graph import StateGraph
from .state import ResumeOptimizerState
from app.services.llm_optimizer import tailor_resume
from app.services.llm_ats import ats_score
from app.services.llm_improver import improve_resume
from app.services.docx_generator import generate_final_docx
import os
import uuid

# ---------------------------------------------------
# ENABLE LOGGING
# ---------------------------------------------------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("optimizer")


ATS_THRESHOLD = 98
MAX_LOOPS = 2


# ---------------------------------------------------
# NODES
# ---------------------------------------------------

def node_tailor(state: ResumeOptimizerState):
    log.info("=== NODE: TAILOR ===")
    log.info("Original sections:\n%s", state.resume_sections)

    tailored = tailor_resume(
        state.resume_sections,
        state.job_description,
        state.original_experience_positions
    )

    state.resume_sections["summary"] = tailored["summary"]
    state.resume_sections["experience"] = tailored["experience"]
    state.resume_sections["skills"] = tailored["skills"]

    state.resume_sections["education"] = state.original_education

    log.info("Tailored summary:\n%s", state.resume_sections["summary"])
    log.info("Tailored skills:\n%s", state.resume_sections["skills"])

    return state


def node_ats(state: ResumeOptimizerState):
    log.info("=== NODE: ATS SCORE ===")
    result = ats_score(state.resume_sections, state.job_description)

    state.ats_score = result["score"]
    state.analysis = result["analysis"]

    log.info("ATS Score: %s", state.ats_score)
    log.info("ATS Analysis: %s", state.analysis)

    return state


def check_score(state: ResumeOptimizerState):
    log.info("=== CHECK SCORE ===")
    log.info(f"Current Score = {state.ats_score}, Threshold = {ATS_THRESHOLD}, Iteration = {state.iteration_count}")

    if state.ats_score >= ATS_THRESHOLD:
        log.info("Decision: PASS (threshold met)")
        return "PASS"

    if state.iteration_count >= MAX_LOOPS:
        log.info("Decision: STOP (max loops reached)")
        return "STOP"

    log.info("Decision: IMPROVE (score too low, more loops allowed)")
    return "IMPROVE"


def node_improve(state: ResumeOptimizerState):
    log.info("=== NODE: IMPROVE ===")
    log.info("Applying ATS analysis improvements...")

    improved = improve_resume(
        state.resume_sections,
        state.analysis,
        state.job_description,
        state.original_experience_positions
    )

    state.resume_sections["summary"] = improved["summary"]
    state.resume_sections["experience"] = improved["experience"]
    state.resume_sections["skills"] = improved["skills"]
    state.resume_sections["education"] = state.original_education

    state.iteration_count += 1

    log.info(f"New iteration count: {state.iteration_count}")
    log.info("Improved summary:\n%s", state.resume_sections["summary"])
    log.info("Improved skills:\n%s", state.resume_sections["skills"])

    return state


def node_generate(state: ResumeOptimizerState):
    log.info("=== NODE: GENERATE DOCX ===")
    log.info("Final score = %s, Passed = %s", state.ats_score, state.passed)

    os.makedirs("generated", exist_ok=True)

    unique_filename = f"final_resume_{uuid.uuid4()}.docx"
    output_path = f"generated/{unique_filename}"

    user_info = {
        "full_name": state.full_name,
        "phone": state.phone,
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

    log.info(f"Generated resume at: {output_path}")

    return state


# ---------------------------------------------------
# BUILD THE GRAPH
# ---------------------------------------------------

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