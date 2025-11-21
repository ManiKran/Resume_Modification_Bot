from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TAILOR_PROMPT = """
You are a resume tailoring expert.

You will receive:
- Original SUMMARY, EXPERIENCE, SKILLS
- DO NOT modify EDUCATION.
- In EXPERIENCE:
    * DO NOT modify job titles.
    * DO NOT modify company names.
    * DO NOT modify dates.
    * Only rewrite bullet points to match job description.
- IN SUMMARY and SKILLS:
    * You may rewrite fully to match the job description.
- Keep content truthful. No hallucinations.

Your output MUST be valid JSON with the following structure:

{
  "summary": "string",
  "experience": [
     {
       "company": "string",
       "title": "string",
       "location": "string",
       "dates": "string",
       "bullets": ["string", ...]
     }
  ],
  "skills": {
      "Technical Skills": ["Python", "Node.js", ...],
      "AI/ML Skills": ["RAG", "Embeddings", ...],
      "Tools": ["Azure OpenAI", "Vertex AI", ...]
  }
}

RULES FOR SKILLS:
- Skills MUST be a dictionary.
- Keys = categories.
- Values = lists of skills.
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