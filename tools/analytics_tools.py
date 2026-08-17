"""
Analytics Tools - Tools for institutional analytics and advisor dashboards.

These tools provide aggregated analytics for administrators and
student summaries for academic advisors, powered by BigQuery.
"""

from google.cloud.bigquery import ScalarQueryParameter

from edupulse import config
from tools.bq_client import query_bigquery

DATASET = config.BIGQUERY_DATASET_STUDENT
ANALYTICS_DATASET = config.BIGQUERY_DATASET_ANALYTICS


def get_institutional_analytics(time_period: str = "current_semester") -> dict:
    """Get aggregated institutional analytics for administrators.

    Args:
        time_period: The time period to analyze (current_semester, last_semester, year_to_date).

    Returns:
        dict with aggregated metrics including retention_rate, attrition_rate, and risk_distribution.
    """
    total = query_bigquery(f"SELECT COUNT(*) as cnt FROM `{DATASET}.students`")[0]["cnt"]

    risk_dist = query_bigquery(f"""
        SELECT risk_level, COUNT(*) as cnt
        FROM `{DATASET}.risk_scores`
        GROUP BY risk_level
    """)
    risk_map = {r["risk_level"]: r["cnt"] for r in risk_dist}

    dept_breakdown = query_bigquery(f"""
        SELECT department, AVG(retention_rate) as retention, SUM(total_students) as enrollment
        FROM `{ANALYTICS_DATASET}.department_comparison`
        GROUP BY department
    """)

    trends = query_bigquery(f"""
        SELECT semester, AVG(retention_rate) as retention
        FROM `{ANALYTICS_DATASET}.retention_trends`
        GROUP BY semester
        ORDER BY semester DESC
        LIMIT 4
    """)

    low = risk_map.get("low", 0)
    med = risk_map.get("medium", 0)
    high = risk_map.get("high", 0)
    crit = risk_map.get("critical", 0)
    at_risk = med + high + crit

    return {
        "time_period": time_period,
        "total_students": total,
        "retention_rate": round((total - at_risk) / total, 2) if total > 0 else 0,
        "attrition_rate": round(at_risk / total, 2) if total > 0 else 0,
        "risk_distribution": {"low": low, "medium": med, "high": high, "critical": crit},
        "department_breakdown": dept_breakdown,
        "trends": list(reversed(trends)),
    }


def get_advisor_students(advisor_id: str) -> dict:
    """Get a list of students assigned to a specific academic advisor.

    Args:
        advisor_id: The unique advisor identifier.

    Returns:
        dict with assigned students, their risk levels, and summary data.
    """
    rows = query_bigquery(
        f"""
        SELECT
            s.student_id, s.name, s.gpa,
            r.risk_level, r.risk_score, r.contributing_factors
        FROM `{DATASET}.students` s
        LEFT JOIN `{DATASET}.risk_scores` r ON s.student_id = r.student_id
        WHERE s.advisor_id = @advisor_id
    """,
        [ScalarQueryParameter("advisor_id", "STRING", advisor_id)],
    )
    if not rows:
        return {"advisor_id": advisor_id, "error": f"No students found for advisor {advisor_id}."}

    students = [
        {
            "student_id": r["student_id"],
            "name": r["name"],
            "gpa": r.get("gpa"),
            "risk_level": r.get("risk_level", "unknown"),
            "risk_score": r.get("risk_score"),
            "top_concern": (
                (r.get("contributing_factors") or "").split("|")[0] if r.get("contributing_factors") else "None"
            ),
        }
        for r in rows
    ]
    return {
        "advisor_id": advisor_id,
        "assigned_students": students,
        "total_students": len(students),
        "critical_count": sum(1 for s in students if s["risk_level"] == "critical"),
        "high_count": sum(1 for s in students if s["risk_level"] == "high"),
        "medium_count": sum(1 for s in students if s["risk_level"] == "medium"),
        "low_count": sum(1 for s in students if s["risk_level"] == "low"),
    }


def get_retention_trends(department: str | None = None, semesters: int = 4) -> dict:
    """Get retention and attrition trends over multiple semesters.

    Args:
        department: Optional department filter. If None, returns institution-wide data.
        semesters: Number of semesters to include in the trend analysis.

    Returns:
        dict with trend data showing retention rates over time.
    """
    if department:
        trends = query_bigquery(
            f"""
            SELECT semester, retention_rate as retention, enrolled_count as enrollment
            FROM `{ANALYTICS_DATASET}.retention_trends`
            WHERE department = @department
            ORDER BY semester DESC
            LIMIT {semesters}
        """,
            [ScalarQueryParameter("department", "STRING", department)],
        )
    else:
        trends = query_bigquery(f"""
            SELECT semester, AVG(retention_rate) as retention, SUM(enrolled_count) as enrollment
            FROM `{ANALYTICS_DATASET}.retention_trends`
            GROUP BY semester
            ORDER BY semester DESC
            LIMIT {semesters}
        """)

    return {
        "department": department or "Institution-wide",
        "semesters_analyzed": len(trends),
        "trends": list(reversed(trends)),
    }


def get_department_comparison() -> dict:
    """Compare retention and attrition metrics across all departments.

    Returns:
        dict with department-level comparison data for administrative decision making.
    """
    rows = query_bigquery(f"""
        SELECT
            department,
            retention_rate as retention,
            (1 - retention_rate) as attrition,
            total_students as enrollment,
            at_risk_count as at_risk
        FROM `{ANALYTICS_DATASET}.department_comparison`
        ORDER BY retention_rate DESC
    """)
    if not rows:
        return {"departments": [], "error": "No department data found."}

    best = rows[0]
    worst = rows[-1]
    return {
        "departments": rows,
        "highest_retention": f"{best['department']} ({best['retention']:.0%})",
        "lowest_retention": f"{worst['department']} ({worst['retention']:.0%})",
        "recommendation": f"Focus retention resources on {worst['department']} department",
    }
