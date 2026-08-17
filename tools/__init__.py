"""
EduPulse Tools Module

Custom tools for the EduPulse multi-agent system.
"""

from .analytics_tools import (
    get_advisor_students,
    get_department_comparison,
    get_institutional_analytics,
    get_retention_trends,
)
from .datastore_tools import (
    add_advisor_note,
    get_active_alerts,
    get_student_realtime_engagement,
)
from .risk_tools import (
    analyze_student_risk,
    get_intervention_recommendations,
    get_student_academic_profile,
    get_student_engagement_metrics,
)

__all__ = [
    "add_advisor_note",
    "analyze_student_risk",
    "get_active_alerts",
    "get_advisor_students",
    "get_department_comparison",
    "get_institutional_analytics",
    "get_intervention_recommendations",
    "get_retention_trends",
    "get_student_academic_profile",
    "get_student_engagement_metrics",
    "get_student_realtime_engagement",
]
