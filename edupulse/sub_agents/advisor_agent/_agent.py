"""Advisor Agent - Advisor Dashboard and Student Summaries."""

from google.adk.agents import LlmAgent

from . import prompt
from edupulse import config
from tools.analytics_tools import get_advisor_students
from tools.datastore_tools import (
    add_advisor_note,
    get_active_alerts,
    get_student_realtime_engagement,
)
from tools.risk_tools import analyze_student_risk, get_intervention_recommendations

MODEL = config.MODEL_ADVISOR

advisor_agent = LlmAgent(
    name="AdvisorAgent",
    model=MODEL,
    description="Provides advisors with student summaries and intervention recommendations",
    instruction=prompt.ADVISOR_AGENT_PROMPT,
    tools=[
        get_advisor_students,
        analyze_student_risk,
        get_intervention_recommendations,
        get_student_realtime_engagement,
        get_active_alerts,
        add_advisor_note,
    ],
)
