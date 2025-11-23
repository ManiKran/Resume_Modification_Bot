from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TAILOR_PROMPT = """
You are a resume tailoring expert.

INPUT YOU RECEIVE:
- Original SUMMARY, EXPERIENCE, SKILLS
- Job Description
- Protected experience fields: 
    * DO NOT change job titles, company names, locations, or dates.
    * Only rewrite bullet points.

ALLOWED CHANGES:
- SUMMARY → you may fully rewrite, but it MUST be strictly under **630 characters**.
- EXPERIENCE → only rewrite bullet points.
- SKILLS → rewrite freely to fit the job description.
- EDUCATION → do NOT modify.

HARD CONSTRAINTS FOR EXPERIENCE BULLETS:
- The FIRST experience must contain **exactly 8 bullet points**.
- The SECOND experience must contain **exactly 6 bullet points**.
- The THIRD experience must contain **exactly 5 bullet points**.
- If the resume has fewer experiences, follow the rule only for available ones.
- If it has more than 3 experiences, only enforce this rule for the first 3; leave the rest unchanged.
- All bullets must be rewritten to align with the job description while staying truthful.

JSON OUTPUT RULES:
You MUST return valid JSON ONLY in the following structure:

{
  "summary": "<string less than 630 characters>",
  "experience": [
     {
       "company": "string",
       "title": "string",
       "location": "string",
       "dates": "string",
       "bullets": ["string", ...]   // must match bullet count rules
     }
  ],
  "skills": {
      "Technical Skills": ["Python", "Node.js", ...],
      "AI/ML Skills": ["RAG", "Embeddings", ...],
      "Tools": ["Azure OpenAI", "Vertex AI", ...]
  }
}

ADDITIONAL RULES:
- Output MUST be valid JSON with no comments.
- Escape all internal quotes using \\" inside JSON strings.
- Absolutely no text outside the JSON object.
"""

def tailor_resume(original_sections, job_description, experience_locks):
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": TAILOR_PROMPT},
            {
                "role": "user",
                "content": f"""
Original Sections: {original_sections}
Job Description: {job_description}
Protected Experience Info (DO NOT CHANGE): {experience_locks}
"""
            }
        ]
    )

    return eval(response.choices[0].message.content)