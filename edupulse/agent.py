"""EduPulse Root Agent - Orchestrator."""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from . import config, prompt
from .empty_output import ensure_non_empty_response
from .model_armor import create_model_armor_guard
from .sub_agents.student_agent import student_agent
from .sub_agents.risk_predictor_agent import risk_predictor_agent
from .sub_agents.course_recommender_agent import course_recommender_agent
from .sub_agents.financial_aid_agent import financial_aid_agent
from .sub_agents.advisor_agent import advisor_agent
from .sub_agents.admin_agent import admin_agent

_model_armor_guard = create_model_armor_guard()

root_agent = LlmAgent(
    name="EduPulse",
    model=config.MODEL,
    description="Main orchestrator for the EduPulse Student Success AI Platform",
    instruction=prompt.EDUPULSE_COORDINATOR_PROMPT,
    tools=[
        AgentTool(agent=student_agent),
        AgentTool(agent=risk_predictor_agent),
        AgentTool(agent=course_recommender_agent),
        AgentTool(agent=financial_aid_agent),
        AgentTool(agent=advisor_agent),
        AgentTool(agent=admin_agent),
    ],
    before_model_callback=_model_armor_guard.before_model_callback if _model_armor_guard else None,
    after_model_callback=[
        *([_model_armor_guard.after_model_callback] if _model_armor_guard else []),
        ensure_non_empty_response,
    ],
)
