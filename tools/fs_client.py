"""
Firestore Client - Shared Firestore client for real-time EduPulse data.
"""

from google.cloud import firestore

from edupulse import config

PROJECT_ID = config.PROJECT_ID

_client = None


def get_firestore_client():
    """Get or create a Firestore client singleton."""
    global _client
    if _client is None:
        _client = firestore.Client(project=PROJECT_ID)
    return _client


# Collection names
COLLECTION_ENGAGEMENT = config.COLLECTION_ENGAGEMENT
COLLECTION_SESSIONS = config.COLLECTION_SESSIONS
COLLECTION_ALERTS = config.COLLECTION_ALERTS
COLLECTION_ADVISOR_NOTES = config.COLLECTION_ADVISOR_NOTES
