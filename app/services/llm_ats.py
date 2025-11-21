from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ATS_PROMPT = """
You are an ATS scoring engine.
Given resume sections and job description, return:

{
  "score": <number 0-100>,
  "analysis": {
    "missing_keywords": [...],
    "weak_areas": "...",
    "recommendations": "..."
  }
}
"""

def ats_score(sections, jd):
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": ATS_PROMPT},
            {"role": "user", "content": f"Resume Sections: {sections}"},
            {"role": "user", "content": f"Job Description: {jd}"}
        ]
    )
    return eval(resp.choices[0].message.content)