"""Risk Predictor Agent - Student Attrition Prediction."""

from google.adk.agents import LlmAgent

from . import prompt
from edupulse import config
from tools.risk_tools import (
    analyze_student_risk,
    get_intervention_recommendations,
    get_student_academic_profile,
    get_student_engagement_metrics,
)

MODEL = config.MODEL_RISK_PREDICTOR

risk_predictor_agent = LlmAgent(
    name="RiskPredictor",
    model=MODEL,
    description="Analyzes student data to predict attrition risk and recommend interventions",
    instruction=prompt.RISK_PREDICTOR_PROMPT,
    tools=[
        analyze_student_risk,
        get_student_academic_profile,
        get_student_engagement_metrics,
        get_intervention_recommendations,
    ],
)
