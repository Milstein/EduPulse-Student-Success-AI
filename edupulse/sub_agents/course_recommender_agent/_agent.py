"""Course Recommender Agent - Academic Pathway Recommendations."""

from google.adk.agents import LlmAgent

from . import prompt
from edupulse import config

MODEL = config.MODEL_COURSE_RECOMMENDER


def search_course_catalog(query: str) -> dict:
    """Search the course catalog for courses, prerequisites, and degree requirements.

    Args:
        query: The search query about courses, prerequisites, degree requirements, or scheduling.

    Returns:
        dict with relevant course information.
    """
    return {
        "status": "success",
        "results": [
            "CS 101 - Intro to Computer Science (3cr, no prereqs)",
            "CS 201 - Data Structures and Algorithms (3cr, prereqs: CS 101, MATH 151)",
            "CS 301 - Database Systems (3cr, prereq: CS 201)",
            "CS 350 - Operating Systems (3cr, prereqs: CS 201, CS 250)",
            "CS 400 - Software Engineering (3cr, prereq: CS 301)",
            "CS 450 - Artificial Intelligence (3cr, prereqs: CS 301, MATH 251)",
        ],
    }


course_recommender_agent = LlmAgent(
    name="CourseRecommender",
    model=MODEL,
    description="Recommends courses based on degree requirements and student performance",
    instruction=prompt.COURSE_RECOMMENDER_PROMPT,
    tools=[search_course_catalog],
)
