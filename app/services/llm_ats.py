import json
import re
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ATS_PROMPT = """
You are an ATS scoring engine.
You MUST respond ONLY with valid JSON.
NO comments, NO explanations, NO trailing commas.

The output MUST follow this format exactly:

{
  "score": 0-100,
  "analysis": {
    "missing_keywords": ["keyword1", "keyword2"],
    "weak_areas": "string",
    "recommendations": "string"
  }
}
"""

def safe_json_loads(text: str):
    """
    Attempts to safely parse LLM output by cleaning:
    - Removes JS-style comments
    - Removes trailing commas
    - Fixes single quotes → double quotes
    """

    # Remove JS-style comments
    text = re.sub(r"//.*", "", text)

    # Replace single quotes with double
    # (JSON requires double quotes)
    text = text.replace("'", '"')

    # Remove trailing commas before closing braces/brackets
    text = re.sub(r",(\s*[}\]])", r"\1", text)

    # Strip whitespace
    text = text.strip()

    # Try JSON parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Last resort: extract JSON substring
        match = re.search(r"{.*}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass

        raise ValueError(f"Could not parse LLM JSON output:\n{text}")


def ats_score(sections, jd):
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": ATS_PROMPT},
            {"role": "user", "content": f"Resume Sections: {json.dumps(sections)}"},
            {"role": "user", "content": f"Job Description: {jd}"}
        ]
    )

    raw_output = resp.choices[0].message.content

    # Safely parse the JSON
    return safe_json_loads(raw_output)