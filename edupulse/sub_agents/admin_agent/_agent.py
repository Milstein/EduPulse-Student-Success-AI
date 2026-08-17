"""Admin Agent - Institution-Wide Analytics."""

from google.adk.agents import LlmAgent

from . import prompt
from edupulse import config
from tools.analytics_tools import (
    get_department_comparison,
    get_institutional_analytics,
    get_retention_trends,
)

MODEL = config.MODEL_ADMIN

admin_agent = LlmAgent(
    name="AdminAgent",
    model=MODEL,
    description="Provides institution-wide analytics and retention metrics",
    instruction=prompt.ADMIN_AGENT_PROMPT,
    tools=[
        get_institutional_analytics,
        get_retention_trends,
        get_department_comparison,
    ],
)
