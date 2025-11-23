from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

IMPROVE_PROMPT = """
You are a resume refinement expert.

==============================
RULES
==============================
- DO NOT modify EDUCATION.
- In EXPERIENCE:
    * DO NOT change job titles.
    * DO NOT change company names.
    * DO NOT change dates.
    * ONLY rewrite bullet points.

==============================
STRUCTURE REQUIREMENTS
==============================
You MUST return valid JSON ONLY in this exact structure:

{
  "summary": "string (strictly less than 630 characters)",
  "experience": [
     {
       "company": "string",
       "title": "string",
       "location": "string",
       "dates": "string",
       "bullets": ["string", ...]   ← MUST follow exact bullet rules below
     }
  ],
  "skills": {
      "Technical Skills": ["Python", "SQL", ...],
      "AI/ML Skills": ["RAG", "Fine-tuning", ...],
      "Tools": ["Azure", "Vertex AI", ...]
  }
}

==============================
BULLET COUNT RULES
==============================
- Experience #1 → EXACTLY **7** bullets.
- Experience #2 → EXACTLY **5** bullets.
- Experience #3 → EXACTLY **4** bullets.
- If resume has fewer jobs, apply rule only to existing ones.

==============================
SKILLS RULES
==============================
- SKILLS MUST ALWAYS be a JSON OBJECT (dictionary).
- Keys = skill categories
- Values = lists of strings
- NEVER return a list for skills.

==============================
SUMMARY RULES
==============================
- Summary MUST be strictly less than 630 characters.

==============================
OUTPUT
==============================
Return ONLY valid JSON. No explanations, no comments.
"""


def safe_json_parse(text: str):
    """
    Safely parse JSON returned by the LLM.
    Attempts:
    1. direct json.loads
    2. remove ```json wrappers
    3. fallback minimal fixes
    """
    try:
        return json.loads(text)
    except:
        pass

    # Remove code block wrappers
    if "```" in text:
        cleaned = text.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except:
            pass

    # LAST RESORT FIXES
    cleaned = text.replace("\n", " ").replace("\t", " ")

    try:
        return json.loads(cleaned)
    except:
        raise ValueError(f"LLM returned invalid JSON:\n{text}")


def ensure_skills_dict(skills):
    """Guarantee skills are a dictionary."""
    if isinstance(skills, dict):
        return skills

    # If it's a list → convert to a fallback dict
    if isinstance(skills, list):
        return {"General Skills": skills}

    # If it's something else → fallback
    return {"General Skills": ["Problem Solving", "Communication"]}


def enforce_bullet_rules(experience):
    """Fix bullet counts to match (7, 5, 4)."""
    required = [7, 5, 4]

    for i, job in enumerate(experience):
        if i >= len(required):
            break  # only enforce first 3 jobs

        need = required[i]
        bullets = job.get("bullets", [])

        # Expand / trim bullets to required length
        if len(bullets) < need:
            bullets += ["• Additional impact bullet needed"] * (need - len(bullets))
        elif len(bullets) > need:
            bullets = bullets[:need]

        job["bullets"] = bullets

    return experience


def enforce_summary_length(summary):
    """Ensure summary is < 630 chars."""
    if len(summary) <= 630:
        return summary
    return summary[:627] + "..."


def improve_resume(sections, analysis, jd, experience_locks):
    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": IMPROVE_PROMPT},
            {
                "role": "user",
                "content": f"""
Resume Sections: {sections}
ATS Analysis: {analysis}
Job Description: {jd}
Protected Experience Info: {experience_locks}
"""
            }
        ]
    )

    raw_output = resp.choices[0].message.content

    parsed = safe_json_parse(raw_output)

    # --- Enforce skill dictionary ---
    parsed["skills"] = ensure_skills_dict(parsed.get("skills"))

    # --- Enforce bullet count rules ---
    parsed["experience"] = enforce_bullet_rules(parsed.get("experience", []))

    # --- Enforce summary length ---
    parsed["summary"] = enforce_summary_length(parsed.get("summary", ""))

    return parsed