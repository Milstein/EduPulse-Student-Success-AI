"""
Risk Prediction Tools - Tools for analyzing student attrition risk.

These tools analyze student data from BigQuery to identify at-risk students
and recommend personalized interventions.
"""

from google.cloud.bigquery import ScalarQueryParameter

from edupulse import config
from tools.bq_client import query_bigquery

DATASET = config.BIGQUERY_DATASET_STUDENT


def analyze_student_risk(student_id: str) -> dict:
    """Analyze a student's attrition risk based on academic, engagement, financial, and personal factors.

    Args:
        student_id: The unique student identifier to analyze.

    Returns:
        dict containing risk_score, risk_level, contributing_factors, and recommendations.
    """
    rows = query_bigquery(
        f"""
        SELECT
            s.student_id,
            s.name,
            s.gpa,
            s.credits_completed,
            s.credits_attempted,
            r.risk_score,
            r.risk_level,
            r.contributing_factors,
            r.recommendations
        FROM `{DATASET}.students` s
        LEFT JOIN `{DATASET}.risk_scores` r ON s.student_id = r.student_id
        WHERE s.student_id = @student_id
        LIMIT 1
    """,
        [ScalarQueryParameter("student_id", "STRING", student_id)],
    )
    if not rows:
        return {"student_id": student_id, "error": f"Student {student_id} not found."}
    row = rows[0]
    return {
        "student_id": row["student_id"],
        "student_name": row["name"],
        "risk_score": row.get("risk_score"),
        "risk_level": row.get("risk_level"),
        "current_gpa": row.get("gpa"),
        "contributing_factors": (
            row.get("contributing_factors", "").split("|") if row.get("contributing_factors") else []
        ),
        "recommendations": (row.get("recommendations", "").split("|") if row.get("recommendations") else []),
    }


def get_student_academic_profile(student_id: str) -> dict:
    """Retrieve a student's academic profile including GPA, courses, and performance trends.

    Args:
        student_id: The unique student identifier.

    Returns:
        dict with academic profile data including GPA, course history, and trends.
    """
    rows = query_bigquery(
        f"""
        SELECT
            student_id, name, gpa, credits_completed, credits_attempted, major, year, enrollment_status
        FROM `{DATASET}.students`
        WHERE student_id = @student_id
    """,
        [ScalarQueryParameter("student_id", "STRING", student_id)],
    )
    if not rows:
        return {"student_id": student_id, "error": f"Student {student_id} not found."}
    row = rows[0]
    attempted = row.get("credits_attempted", 0) or 0
    completed = row.get("credits_completed", 0) or 0
    return {
        "student_id": row["student_id"],
        "student_name": row["name"],
        "current_gpa": row.get("gpa"),
        "major": row.get("major"),
        "year": row.get("year"),
        "enrollment_status": row.get("enrollment_status"),
        "credits_completed": completed,
        "credits_attempted": attempted,
        "completion_rate": round(completed / attempted, 2) if attempted > 0 else 0,
    }


def get_student_engagement_metrics(student_id: str) -> dict:
    """Retrieve a student's engagement metrics from the LMS and campus systems.

    Args:
        student_id: The unique student identifier.

    Returns:
        dict with engagement data including LMS activity, attendance, and participation.
    """
    rows = query_bigquery(
        f"""
        SELECT
            e.student_id,
            s.name,
            AVG(e.attendance_rate) as avg_attendance,
            COUNT(e.enrollment_id) as courses_enrolled
        FROM `{DATASET}.enrollments` e
        JOIN `{DATASET}.students` s ON e.student_id = s.student_id
        WHERE e.student_id = @student_id
        GROUP BY e.student_id, s.name
    """,
        [ScalarQueryParameter("student_id", "STRING", student_id)],
    )
    if not rows:
        return {"student_id": student_id, "error": f"Student {student_id} not found."}
    row = rows[0]
    return {
        "student_id": row["student_id"],
        "student_name": row["name"],
        "avg_attendance_rate": row.get("avg_attendance"),
        "courses_enrolled": row.get("courses_enrolled"),
    }


def get_intervention_recommendations(risk_level: str, factors: list) -> dict:
    """Generate personalized intervention recommendations based on risk level and contributing factors.

    Args:
        risk_level: The risk level (low, medium, high, critical).
        factors: List of contributing risk factors identified in the analysis.

    Returns:
        dict with prioritized intervention recommendations and timelines.
    """
    interventions = {
        "low": {
            "timeline": "next 30 days",
            "actions": [
                "Positive reinforcement check-in",
                "Encourage continued engagement",
                "Monitor GPA trends",
            ],
        },
        "medium": {
            "timeline": "next 14 days",
            "actions": [
                "Scheduled advisor meeting",
                "Tutoring referral",
                "Attendance follow-up",
            ],
        },
        "high": {
            "timeline": "within 7 days",
            "actions": [
                "Immediate advisor outreach",
                "Mandatory tutoring enrollment",
                "Academic probation review",
                "Financial aid status check",
            ],
        },
        "critical": {
            "timeline": "within 48 hours",
            "actions": [
                "URGENT: Dean of students outreach",
                "Emergency services assessment",
                "Academic standing review",
                "Financial emergency fund evaluation",
                "Mental health referral",
            ],
        },
    }

    plan = interventions.get(risk_level, interventions["medium"])
    return {
        "risk_level": risk_level,
        "factors": factors,
        "priority_actions": plan["actions"],
        "timeline": plan["timeline"],
    }
