from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

IMPROVE_PROMPT = """
You are a resume refinement expert with strict ATS optimization AND strict historical accuracy.

==============================
MANDATORY RULES
==============================
- DO NOT modify EDUCATION.
- In EXPERIENCE:
    * DO NOT change job titles.
    * DO NOT change company names.
    * DO NOT change locations.
    * DO NOT change dates.
    * ONLY rewrite bullet points.

==============================
SUMMARY RULES
==============================
- Summary MUST be strictly less than 800 characters.
- Summary MUST incorporate missing_keywords from ATS analysis naturally and truthfully.
- Summary MUST reflect the strengths recommended in ATS analysis.

==============================
BULLET COUNT RULES
==============================
Enforce EXACT bullet counts:
- Experience #1 → 7 bullets
- Experience #2 → 6 bullets
- Experience #3 → 4 bullets

==============================
TIME-PERIOD ACCURACY (CRITICAL)
==============================
For EACH job:

1. Read the date range from the "dates" field.
2. Only include tools/technologies/frameworks that existed and were publicly available during THAT date range.
3. Examples of OFF-LIMITS technologies before their release dates:
   - GPT-4 → 2023+
   - GPT-3 → 2020+
   - LangChain → 2023+
   - Azure OpenAI → 2021+
   - Vertex AI → 2021+
   - Amazon Bedrock → 2023+
   - HuggingFace Transformers → 2018+
   - AWS Lambda → 2015+
   - Cloud Run → 2019+
4. If JD requires a modern tool that DID NOT exist during that experience:
   → DO NOT add it.
   Instead add a historically realistic alternative (e.g., “custom NLP pipeline in Python”)

==============================
ATS OPTIMIZATION RULES
==============================
You MUST use ALL of the following from ATS analysis:

1. missing_keywords  
   → MUST appear in summary or bullets or skills

2. weak_areas  
   → MUST be improved explicitly through rewritten bullets

3. recommendations  
   → MUST be implemented in the rewrite

Do NOT fabricate experience, but you may highlight truthful missing competencies.

==============================
SKILLS RULES
==============================
- SKILLS MUST ALWAYS BE A JSON OBJECT.
- Keys = category names
- Values = lists of strings.
- Include missing_keywords if they are skills/tools.

==============================
OUTPUT FORMAT
==============================
Return ONLY valid JSON. NO text outside the JSON.
Format:

{
  "summary": "",
  "experience": [...],
  "skills": {}
}
"""

def safe_json_parse(text: str):
    try:
        return json.loads(text)
    except:
        pass

    if "```" in text:
        cleaned = text.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except:
            pass

    cleaned = text.replace("\n", " ").replace("\t", " ")
    try:
        return json.loads(cleaned)
    except:
        raise ValueError(f"LLM returned invalid JSON:\n{text}")

def ensure_skills_dict(skills):
    if isinstance(skills, dict):
        return skills
    if isinstance(skills, list):
        return {"General Skills": skills}
    return {"General Skills": ["Problem Solving", "Communication"]}

def enforce_bullet_rules(experience):
    required = [7, 6, 4]
    for i, job in enumerate(experience):
        if i >= len(required):
            break
        need = required[i]
        bullets = job.get("bullets", [])
        if len(bullets) < need:
            bullets += ["• Additional impact bullet needed"] * (need - len(bullets))
        elif len(bullets) > need:
            bullets = bullets[:need]
        job["bullets"] = bullets
    return experience

def enforce_summary_length(summary):
    if len(summary) <= 800:
        return summary
    return summary[:797] + "..."

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

    parsed["skills"] = ensure_skills_dict(parsed.get("skills"))
    parsed["experience"] = enforce_bullet_rules(parsed.get("experience", []))
    parsed["summary"] = enforce_summary_length(parsed.get("summary", ""))

    return parsed