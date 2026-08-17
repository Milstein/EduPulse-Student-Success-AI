"""
Data Store Tools - Tools for real-time student data via Firestore.

These tools provide access to real-time student engagement data,
active alerts, and advisor notes stored in Firestore.
"""

from tools.fs_client import (
    COLLECTION_ADVISOR_NOTES,
    COLLECTION_ALERTS,
    COLLECTION_ENGAGEMENT,
    get_firestore_client,
)


def get_student_realtime_engagement(student_id: str) -> dict:
    """Get real-time engagement data for a student from Firestore.

    Args:
        student_id: The unique student identifier.

    Returns:
        dict with real-time engagement metrics (LMS activity, current session, etc.).
    """
    db = get_firestore_client()
    doc = db.collection(COLLECTION_ENGAGEMENT).document(student_id).get()
    if not doc.exists:
        return {"student_id": student_id, "error": "No real-time engagement data found."}
    return {"student_id": student_id, "engagement": doc.to_dict()}


def get_active_alerts(risk_level: str | None = None) -> dict:
    """Get active alerts for at-risk students from Firestore.

    Args:
        risk_level: Optional filter by risk level (critical, high, medium).

    Returns:
        dict with active alerts requiring attention.
    """
    db = get_firestore_client()
    query = db.collection(COLLECTION_ALERTS)
    if risk_level:
        query = query.where("risk_level", "==", risk_level)
    docs = query.order_by("created_at", direction="DESCENDING").limit(50).stream()
    alerts = [{"id": doc.id, **doc.to_dict()} for doc in docs]
    return {"total_alerts": len(alerts), "alerts": alerts}


def add_advisor_note(student_id: str, advisor_id: str, note: str) -> dict:
    """Add an advisor note for a student in Firestore.

    Args:
        student_id: The unique student identifier.
        advisor_id: The advisor adding the note.
        note: The note content.

    Returns:
        dict with status and the note ID.
    """
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_ADVISOR_NOTES).add(
        {
            "student_id": student_id,
            "advisor_id": advisor_id,
            "note": note,
        }
    )
    return {"status": "success", "note_id": doc_ref[1].id}
