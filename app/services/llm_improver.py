from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

IMPROVE_PROMPT = """
You are a resume refinement expert.

Rules:
- DO NOT modify EDUCATION.
- In EXPERIENCE:
    * DO NOT modify job titles, company names, or dates.
    * Only modify bullet points.
- Improve SUMMARY, EXPERIENCE bullets, and SKILLS
- Follow ATS analysis recommendations.

Return JSON with:
summary, experience, skills
"""

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
    return eval(resp.choices[0].message.content)