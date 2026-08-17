"""Shared test fixtures for EduPulse tests."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture
def mock_bigquery_risk():
    """Mock BigQuery for risk_tools module."""
    with patch("tools.risk_tools.query_bigquery") as mock:
        mock.return_value = [
            {
                "student_id": "STU001",
                "name": "Alice Johnson",
                "gpa": 3.2,
                "credits_completed": 45,
                "credits_attempted": 48,
                "risk_score": 35,
                "risk_level": "medium",
                "contributing_factors": "Low attendance|Missing assignments",
                "recommendations": "Advisor meeting|Tutoring referral",
            }
        ]
        yield mock


@pytest.fixture
def mock_bigquery_analytics():
    """Mock BigQuery for analytics_tools module."""
    with patch("tools.analytics_tools.query_bigquery") as mock:
        mock.return_value = [
            {
                "student_id": "STU001",
                "name": "Alice Johnson",
                "gpa": 3.2,
                "risk_level": "medium",
                "risk_score": 35,
                "contributing_factors": "Low attendance",
            }
        ]
        yield mock


@pytest.fixture
def mock_firestore():
    """Mock Firestore client for offline testing."""
    with patch("tools.fs_client.get_firestore_client") as mock:
        client = MagicMock()
        mock.return_value = client

        eng_doc = MagicMock()
        eng_doc.exists = True
        eng_doc.to_dict.return_value = {
            "lms_activity": "active",
            "last_login": "2026-07-24",
            "current_session": True,
        }
        client.collection.return_value.document.return_value.get.return_value = eng_doc

        alert_doc = MagicMock()
        alert_doc.id = "alert-001"
        alert_doc.to_dict.return_value = {
            "student_id": "STU001",
            "risk_level": "high",
            "message": "Low attendance detected",
        }
        mock_stream = client.collection.return_value.where.return_value.order_by.return_value.limit.return_value.stream
        mock_stream.return_value = [alert_doc]

        yield client


@pytest.fixture
def root_agent():
    """Create the root agent for routing tests."""
    from edupulse.agent import root_agent

    return root_agent


@pytest.fixture
def student_agent():
    """Create the student agent for testing."""
    from edupulse.sub_agents.student_agent import student_agent

    return student_agent


@pytest.fixture
def risk_agent():
    """Create the risk predictor agent for testing."""
    from edupulse.sub_agents.risk_predictor_agent import risk_predictor_agent

    return risk_predictor_agent


@pytest.fixture
def advisor_agent():
    """Create the advisor agent for testing."""
    from edupulse.sub_agents.advisor_agent import advisor_agent

    return advisor_agent


@pytest.fixture
def admin_agent():
    """Create the admin agent for testing."""
    from edupulse.sub_agents.admin_agent import admin_agent

    return admin_agent


@pytest.fixture
def course_agent():
    """Create the course recommender agent for testing."""
    from edupulse.sub_agents.course_recommender_agent import course_recommender_agent

    return course_recommender_agent
