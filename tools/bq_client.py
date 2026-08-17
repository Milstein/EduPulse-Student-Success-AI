"""
BigQuery Client - Shared BigQuery client for all EduPulse tools.
"""

from google.cloud import bigquery

from edupulse import config

PROJECT_ID = config.PROJECT_ID
REGION = config.REGION

_client = None


def get_bigquery_client():
    """Get or create a BigQuery client singleton."""
    global _client
    if _client is None:
        _client = bigquery.Client(project=PROJECT_ID, location=REGION)
    return _client


def query_bigquery(query: str, params: list | None = None) -> list[dict]:
    """Execute a BigQuery query and return results as a list of dicts.

    Args:
        query: SQL query with @param placeholders.
        params: List of QueryParameter objects or tuples (name, type, value).
    """
    client = get_bigquery_client()
    job_config = bigquery.QueryJobConfig()
    if params:
        job_config.query_parameters = params
    result = client.query(query, job_config=job_config)
    return [dict(row) for row in result]
