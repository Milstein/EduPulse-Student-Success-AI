"""Central configuration for EduPulse.

Every deployment-specific setting is read from environment variables
(optionally loaded from a local ``.env`` file). Override any value per
deployment without touching code. See ``.env.example`` for the full list.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# --- Google Cloud ---------------------------------------------------------
PROJECT_ID = os.environ.get("PROJECT_ID", "")
REGION = os.environ.get("REGION", "us-east1")

# --- AI model -------------------------------------------------------------
MODEL = os.environ.get("EDUPULSE_MODEL", "gemini-3.5-flash-lite")

# Per-agent model overrides. Each agent has its own independent default and
# can be specialized via its own environment variable.
MODEL_STUDENT = os.environ.get("EDUPULSE_MODEL_STUDENT", "gemini-3.5-flash-lite")
MODEL_RISK_PREDICTOR = os.environ.get("EDUPULSE_MODEL_RISK_PREDICTOR", "gemini-3.5-flash-lite")
MODEL_COURSE_RECOMMENDER = os.environ.get("EDUPULSE_MODEL_COURSE_RECOMMENDER", "gemini-3.5-flash-lite")
MODEL_FINANCIAL_AID = os.environ.get("EDUPULSE_MODEL_FINANCIAL_AID", "gemini-3.5-flash-lite")
MODEL_ADVISOR = os.environ.get("EDUPULSE_MODEL_ADVISOR", "gemini-3.5-flash-lite")
MODEL_ADMIN = os.environ.get("EDUPULSE_MODEL_ADMIN", "gemini-3.5-flash-lite")

# --- BigQuery -------------------------------------------------------------
BIGQUERY_DATASET_STUDENT = os.environ.get("BIGQUERY_DATASET_STUDENT", "edupulse_student_data")
BIGQUERY_DATASET_ANALYTICS = os.environ.get("BIGQUERY_DATASET_ANALYTICS", "edupulse_analytics")

# --- Firestore collections ------------------------------------------------
COLLECTION_ENGAGEMENT = os.environ.get("FIRESTORE_COLLECTION_ENGAGEMENT", "student_engagement")
COLLECTION_SESSIONS = os.environ.get("FIRESTORE_COLLECTION_SESSIONS", "student_sessions")
COLLECTION_ALERTS = os.environ.get("FIRESTORE_COLLECTION_ALERTS", "active_alerts")
COLLECTION_ADVISOR_NOTES = os.environ.get("FIRESTORE_COLLECTION_ADVISOR_NOTES", "advisor_notes")

# --- Observability --------------------------------------------------------
AGENTOPS_API_KEY = os.environ.get("AGENTOPS_API_KEY", "")
