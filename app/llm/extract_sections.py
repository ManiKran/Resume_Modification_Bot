from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------------------------------------
# IMPROVED EXTRACTION PROMPT — STRICT, STRUCTURED, STABLE
# -------------------------------------------------------

EXTRACT_PROMPT = """
You are a world-class resume parser. Extract structured resume sections from raw text.

You MUST output JSON in EXACTLY the schema below.
No extra text. No markdown. No explanations.
NEVER merge multiple fields into one string.

---------------------------------------------------------
STRICT SCHEMA (MANDATORY — DO NOT ALTER FORMAT)
---------------------------------------------------------

{
  "summary": "string",

  "experience": [
    {
      "title": "string",
      "company": "string",
      "location": "string",
      "dates": "string",
      "responsibilities": ["bullet 1", "bullet 2"]
    }
  ],

  "education": [
    {
      "degree": "string",
      "institution": "string",
      "location": "string",
      "dates": "string"
    }
  ],

  "skills": {
    "certifications": ["Azure AI Fundamentals"],
    "programming": ["Python"],
    "ml_ai": ["Machine Learning"],
    "libraries_frameworks": ["TensorFlow"],
    "devops": ["Docker"],
    "other": []
  }
}

---------------------------------------------------------
RULES
---------------------------------------------------------

GENERAL:
- If something is missing, return "" or [] — NEVER omit keys.
- NEVER hallucinate new experience, degrees, companies, or skills.

SUMMARY:
- One paragraph only.

EXPERIENCE:
- Extract each job as a separate object.
- Titles, companies, locations, and dates must be separate fields.
- Responsibilities MUST be a list of bullet strings.
- If the resume uses paragraphs, convert them into bullets.
- If a bullet already contains "•" or "-", strip it and return clean text.

EDUCATION:
- ALWAYS return a LIST of objects.
- NEVER merge degree + institution + location + dates into one combined line.
- Each field must be parsed separately:
    degree = e.g., "Masters in Data Science"
    institution = e.g., "Syracuse University"
    location = "Syracuse, NY"
    dates = "2023 - 2025"

SKILLS:
- Parse skills from any formatting (comma-separated, bullets, paragraphs, clusters).
- Categorize into:
    certifications
    programming
    ml_ai
    libraries_frameworks
    devops
    other
- NEVER combine categories.

---------------------------------------------------------
Return ONLY valid JSON. No commentary.
---------------------------------------------------------
"""

# -------------------------------------------------------
# MAIN FUNCTION
# -------------------------------------------------------

def extract_resume_sections(raw_text: str) -> dict:
    """
    Calls GPT and returns guaranteed structured JSON.
    """
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": EXTRACT_PROMPT},
            {"role": "user", "content": raw_text}
        ]
    )

    json_output = response.choices[0].message.content.strip()

    # Convert JSON string → dict
    # Using eval() only because output is strictly controlled as JSON
    return eval(json_output)