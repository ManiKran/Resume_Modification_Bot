import json
import re
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ATS_PROMPT = """
You are an ATS scoring engine.
You MUST respond ONLY with valid JSON.
Do NOT use any unescaped double quotes inside strings.

If you need to include quotes inside a string, ESCAPE them using \\".

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

def clean_invalid_quotes(text: str) -> str:
    """
    Fix unescaped quotes inside JSON string values.
    Converts:   "text with "BigQuery" inside"
    Into:       "text with \"BigQuery\" inside"
    """

    # Regex: find strings, then escape internal quotes
    def fix_string(match):
        s = match.group(0)
        # skip the first " and last "
        inner = s[1:-1]
        inner = inner.replace('\\"', '"')  # normalize
        inner = inner.replace('"', '\\"')  # escape
        return f"\"{inner}\""

    return re.sub(r'"([^"\\]|\\.)*"', fix_string, text)


def safe_json_loads(text: str):
    """
    Attempts to safely parse LLM output by cleaning:
    - JS-style comments
    - invalid quotes
    - trailing commas
    - extraneous text
    """

    # Remove comments
    text = re.sub(r"//.*", "", text)

    # Remove trailing commas
    text = re.sub(r",(\s*[}\]])", r"\1", text)

    # Escape invalid quotes inside strings
    text = clean_invalid_quotes(text)

    text = text.strip()

    try:
        return json.loads(text)
    except:
        # try extracting only the JSON part
        match = re.search(r"{.*}", text, re.DOTALL)
        if match:
            cleaned = match.group(0)
            try:
                return json.loads(cleaned)
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
    return safe_json_loads(raw_output)