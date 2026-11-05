"""Day 3 final boss: parse a resume into a Candidate object without guessing visa status."""
from datetime import date
from typing import List, Optional   # Python 3.9: Optional[X], not X | None

import anthropic
from pydantic import BaseModel, Field


class Candidate(BaseModel):
    name: str = Field(description="Candidate's full name as written on the resume")
    email: Optional[str] = Field(default=None,
        description="Email address exactly as written, or null if not present")
    current_title: Optional[str] = Field(default=None,
        description="Most recent job title, e.g. 'Senior Software Engineer', or null if not stated")
    years_experience: Optional[float] = Field(default=None,
        description="Total years of professional work experience. Only fill if stated or "
                    "computable from dated roles; otherwise null")
    skills: List[str] = Field(default_factory=list,
        description="Technical skills explicitly listed, e.g. ['React', 'Java', 'Python']; empty list if none")
    location: Optional[str] = Field(default=None,
        description="City and state/country where the candidate lives, e.g. 'Austin, TX', or null")
    needs_visa_sponsorship: Optional[bool] = Field(default=None,
        description="true ONLY if the text explicitly says the candidate needs sponsorship; "
                    "false ONLY if it explicitly says they do not (e.g. 'US citizen', 'green card holder', "
                    "'no sponsorship required'); null in every other case")
    visa_status: Optional[str] = Field(default=None,
        description="Work authorization exactly as written, e.g. 'H-1B', 'F-1 OPT', 'Green card'; "
                    "null if not explicitly stated")


# Claude doesn't know today's date, so "Present" in a resume needs it to compute experience.
SYSTEM_PROMPT = f"""Today's date is {date.today()}.

You extract candidate information from resumes and recruiter notes.

Rules:
- Use only facts explicitly written in the text. Never infer or guess.
- Visa and work authorization: fill needs_visa_sponsorship and visa_status ONLY when
  the text states them directly. Do NOT infer them from the candidate's name,
  nationality, birthplace, university location, languages spoken, or past
  employers. If not stated, return null. Null is the correct answer, not a failure.
- If any other field is not stated, return null (or an empty list for skills)."""

# Test resume (fictional). Trap: "Authorized to work in the US" does NOT mean "no sponsorship needed".
RESUME = """ALEX MORGAN
Dallas, TX | linkedin.com/in/alexmorgan-dev

Full-stack developer transitioning into AI engineering. Authorized to work in the US.

EXPERIENCE
Software Engineer, Brightline Retail (Dallas, TX)        Jan 2023 - Present
- Built React + FastAPI order dashboard used by 40 stores
Junior Developer, CodeNest Labs (Hyderabad, India)        Jun 2020 - Dec 2022
- Maintained Node.js APIs and PostgreSQL schemas

EDUCATION
M.S. Computer Science, University of Texas at Dallas, 2022
B.Tech, JNTU Hyderabad, 2020

SKILLS: Python, JavaScript, React, FastAPI, Node.js, PostgreSQL, Claude API
"""

client = anthropic.Anthropic()
response = client.messages.parse(
    model="claude-opus-5-5",
    max_tokens=16000,
    system=SYSTEM_PROMPT,
    messages=[{"role": "user", "content": RESUME}],
    output_format=Candidate,
)

for field, value in response.parsed_output.model_dump().items():
    print(f"{field:24} = {value!r}")
