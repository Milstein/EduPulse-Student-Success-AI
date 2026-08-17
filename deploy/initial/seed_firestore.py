import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import firestore

load_dotenv(Path(__file__).parent.parent.parent / ".env")

PROJECT_ID = os.environ.get("PROJECT_ID", "")
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "firestore"

COLLECTION_ENGAGEMENT = os.environ.get("FIRESTORE_COLLECTION_ENGAGEMENT", "student_engagement")
COLLECTION_SESSIONS = os.environ.get("FIRESTORE_COLLECTION_SESSIONS", "student_sessions")
COLLECTION_ALERTS = os.environ.get("FIRESTORE_COLLECTION_ALERTS", "active_alerts")
COLLECTION_ADVISOR_NOTES = os.environ.get("FIRESTORE_COLLECTION_ADVISOR_NOTES", "advisor_notes")

db = firestore.Client(project=PROJECT_ID)


def load_json(filename):
    with open(DATA_DIR / filename) as f:
        return json.load(f)


def seed_collection(collection_name, data):
    batch = db.batch()
    for item in data:
        doc_ref = db.collection(collection_name).document()
        batch.set(doc_ref, item)
    batch.commit()
    print(f"  Seeded {collection_name}: {len(data)} documents")


if __name__ == "__main__":
    print("Seeding Firestore...\n")

    engagement = load_json("engagement.json")
    alerts = load_json("alerts.json")
    notes = load_json("notes.json")
    sessions = load_json("sessions.json")

    seed_collection(COLLECTION_ENGAGEMENT, engagement)
    seed_collection(COLLECTION_ALERTS, alerts)
    seed_collection(COLLECTION_ADVISOR_NOTES, notes)
    seed_collection(COLLECTION_SESSIONS, sessions)

    print("\nFirestore seeding complete!")
