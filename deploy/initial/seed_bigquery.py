import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv(Path(__file__).parent.parent.parent / ".env")

PROJECT_ID = os.environ.get("PROJECT_ID", "")
REGION = os.environ.get("REGION", "us-east1")
DATASET_STUDENT = os.environ.get("BIGQUERY_DATASET_STUDENT", "edupulse_student_data")
DATASET_ANALYTICS = os.environ.get("BIGQUERY_DATASET_ANALYTICS", "edupulse_analytics")
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "bigquery"

client = bigquery.Client(project=PROJECT_ID)


def load_json(filename):
    with open(DATA_DIR / filename) as f:
        return json.load(f)


def ensure_dataset(dataset_id):
    """Create dataset if it doesn't exist."""
    dataset_ref = f"{PROJECT_ID}.{dataset_id}"
    try:
        client.get_dataset(dataset_ref)
        print(f"  Dataset {dataset_id} exists")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        client.create_dataset(dataset, exists_ok=True)
        print(f"  Created dataset {dataset_id}")


def seed_table(table_id, data, schema):
    table_ref = f"{PROJECT_ID}.{DATASET_STUDENT}.{table_id}"
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    job = client.load_table_from_json(data, table_ref, job_config=job_config)
    job.result()
    print(f"  Seeded {table_ref}: {len(data)} rows")


def seed_analytics_table(table_id, data, schema):
    table_ref = f"{PROJECT_ID}.{DATASET_ANALYTICS}.{table_id}"
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    job = client.load_table_from_json(data, table_ref, job_config=job_config)
    job.result()
    print(f"  Seeded {table_ref}: {len(data)} rows")


if __name__ == "__main__":
    print("Seeding BigQuery...\n")

    ensure_dataset(DATASET_STUDENT)
    ensure_dataset(DATASET_ANALYTICS)

    students = load_json("students.json")
    risk_scores = load_json("risk_scores.json")
    enrollments = load_json("enrollments.json")
    dept_comparison = load_json("department_comparison.json")
    retention_trends = load_json("retention_trends.json")

    print(f"{DATASET_STUDENT}:")
    seed_table("students", students, [
        bigquery.SchemaField("student_id", "STRING"),
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("email", "STRING"),
        bigquery.SchemaField("major", "STRING"),
        bigquery.SchemaField("year", "STRING"),
        bigquery.SchemaField("gpa", "FLOAT"),
        bigquery.SchemaField("credits_completed", "INTEGER"),
        bigquery.SchemaField("credits_attempted", "INTEGER"),
        bigquery.SchemaField("enrollment_status", "STRING"),
        bigquery.SchemaField("advisor_id", "STRING"),
    ])

    seed_table("risk_scores", risk_scores, [
        bigquery.SchemaField("risk_id", "STRING"),
        bigquery.SchemaField("student_id", "STRING"),
        bigquery.SchemaField("risk_score", "INTEGER"),
        bigquery.SchemaField("risk_level", "STRING"),
        bigquery.SchemaField("contributing_factors", "STRING"),
        bigquery.SchemaField("recommendations", "STRING"),
    ])

    seed_table("enrollments", enrollments, [
        bigquery.SchemaField("enrollment_id", "STRING"),
        bigquery.SchemaField("student_id", "STRING"),
        bigquery.SchemaField("course_id", "STRING"),
        bigquery.SchemaField("semester", "STRING"),
        bigquery.SchemaField("grade", "STRING"),
        bigquery.SchemaField("status", "STRING"),
        bigquery.SchemaField("attendance_rate", "FLOAT"),
    ])

    print(f"\n{DATASET_ANALYTICS}:")
    seed_analytics_table("department_comparison", dept_comparison, [
        bigquery.SchemaField("department", "STRING"),
        bigquery.SchemaField("avg_gpa", "FLOAT"),
        bigquery.SchemaField("retention_rate", "FLOAT"),
        bigquery.SchemaField("graduation_rate", "FLOAT"),
        bigquery.SchemaField("dropout_rate", "FLOAT"),
        bigquery.SchemaField("at_risk_count", "INTEGER"),
        bigquery.SchemaField("total_students", "INTEGER"),
    ])

    seed_analytics_table("retention_trends", retention_trends, [
        bigquery.SchemaField("semester", "STRING"),
        bigquery.SchemaField("retention_rate", "FLOAT"),
        bigquery.SchemaField("enrolled_count", "INTEGER"),
        bigquery.SchemaField("withdrawn_count", "INTEGER"),
        bigquery.SchemaField("department", "STRING"),
    ])

    print("\nBigQuery seeding complete!")
