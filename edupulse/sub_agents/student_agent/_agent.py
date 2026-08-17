"""Student Agent - Front Door for Student Queries."""

from google.adk.agents import LlmAgent

from . import prompt
from edupulse import config

MODEL = config.MODEL_STUDENT


def search_student_knowledge(query: str) -> dict:
    """Search the student knowledge base for campus resources, policies, and deadlines.

    Args:
        query: The search query about student resources, deadlines, policies, or campus life.

    Returns:
        dict with relevant student information.
    """
    return {
        "status": "success",
        "results": [
            "Fall Registration: Early Apr 1 - May 15, Regular Aug 1 - Aug 20, Late Aug 21-27 (with fee)",
            "Spring Registration: Early Nov 1 - Dec 15, Regular Jan 5 - Jan 15, Late Jan 16-20 (with fee)",
            "Grading: A=90-100, B=80-89, C=70-79, D=60-69, F=<60",
            "Academic Probation: GPA below 2.0",
            "Deans List: GPA 3.5+ each semester",
            "Library: Mon-Thu 8am-10pm, Fri 8am-6pm, Sat 10am-4pm",
            "Tutoring Center: Free, Student Services Bldg Room 101",
            "Counseling: Free, confidential, call (555) 123-4567, 24/7 crisis support",
        ],
    }


student_agent = LlmAgent(
    name="StudentAgent",
    model=MODEL,
    description="Handles student queries about courses, campus resources, and academic status",
    instruction=prompt.STUDENT_AGENT_PROMPT,
    tools=[search_student_knowledge],
)
