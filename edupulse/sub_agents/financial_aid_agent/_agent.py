"""Financial Aid Agent - Financial Aid and Scholarship Support."""

from google.adk.agents import LlmAgent

from . import prompt
from edupulse import config

MODEL = config.MODEL_FINANCIAL_AID


def search_financial_aid(query: str) -> dict:
    """Search the financial aid database for aid programs, deadlines, and eligibility.

    Args:
        query: The search query about financial aid, FAFSA, scholarships, or aid eligibility.

    Returns:
        dict with relevant financial aid information.
    """
    return {
        "status": "success",
        "results": [
            "FAFSA opens October 1 each year. Priority deadline: March 1. State deadline: June 30.",
            "Pell Grant: Up to $7,395/year for undergrads with exceptional need.",
            "Federal Work-Study: Part-time campus jobs, up to $5,000/year.",
            "State Merit Scholarship: $2,000/year, requires 3.0 GPA and full-time enrollment.",
            "University Excellence Award: $5,000/year, competitive, requires 3.5 GPA.",
            "Emergency Financial Aid: Up to $1,500, available for unexpected hardship.",
            "Tuition Payment Plan: Split semester into monthly payments, no interest.",
        ],
    }


financial_aid_agent = LlmAgent(
    name="FinancialAidAgent",
    model=MODEL,
    description="Answers financial aid questions and identifies aid eligibility gaps",
    instruction=prompt.FINANCIAL_AID_PROMPT,
    tools=[search_financial_aid],
)
