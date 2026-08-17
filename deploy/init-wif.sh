#!/bin/bash
# Creates Workload Identity Federation pool and provider for GitHub Actions CI/CD.
# Safe to run multiple times — skips everything if resources already exist.

set -uo pipefail

# Load .env file if it exists
if [ -f "$(dirname "$0")/../.env" ]; then
    export $(grep -v '^#' "$(dirname "$0")/../.env" | xargs)
fi

PROJECT_ID="${PROJECT_ID:?ERROR: PROJECT_ID not set. Add it to .env or export it.}"
GITHUB_REPO="${GITHUB_REPO:?ERROR: GITHUB_REPO not set. Add it to .env or export it.}"
POOL_ID="${POOL_ID:-edupulse-gh-actions}"
PROVIDER_ID="${PROVIDER_ID:-edupulse-oidc-provider}"
SERVICE_ACCOUNT_NAME="${SERVICE_ACCOUNT_NAME:-edupulse-agent}"
SA_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Check if pool is active
POOL_STATE=$(gcloud iam workload-identity-pools describe "${POOL_ID}" \
  --project="${PROJECT_ID}" --location="global" \
  --format="value(state)" 2>/dev/null || echo "NOT_FOUND")

# Check if provider is active
PROVIDER_STATE=$(gcloud iam workload-identity-pools providers describe "${PROVIDER_ID}" \
  --project="${PROJECT_ID}" --location="global" \
  --workload-identity-pool="${POOL_ID}" \
  --format="value(state)" 2>/dev/null || echo "NOT_FOUND")

# Check if SA has WIF binding
SA_POLICY=$(gcloud iam service-accounts get-iam-policy "${SA_EMAIL}" \
  --project="${PROJECT_ID}" 2>/dev/null || echo "")

if [ "${POOL_STATE}" = "ACTIVE" ] && \
   [ "${PROVIDER_STATE}" = "ACTIVE" ] && \
   echo "${SA_POLICY}" | grep -q "workloadIdentityUser"; then
  echo "WIF already fully configured. Nothing to do."
  exit 0
fi

# --- Pool ---
echo "=== Ensuring WIF pool: ${POOL_ID} ==="
if [ "${POOL_STATE}" = "ACTIVE" ]; then
  echo "Pool already exists and active. Skipping."
elif [ "${POOL_STATE}" = "DISABLED" ]; then
  echo "Pool exists but is disabled. Enabling..."
  gcloud iam workload-identity-pools enable "${POOL_ID}" \
    --project="${PROJECT_ID}" --location="global"
elif [ "${POOL_STATE}" = "DELETED" ]; then
  echo "ERROR: Pool was soft-deleted. Must wait 30 days or use a different name."
  exit 1
else
  echo "Creating pool..."
  gcloud iam workload-identity-pools create "${POOL_ID}" \
    --project="${PROJECT_ID}" \
    --location="global" \
    --display-name="EduPulse GitHub Actions Pool" \
    --description="WIF pool for EduPulse GitHub Actions CI/CD"
  echo "Pool created."
fi

# --- Provider ---
echo ""
echo "=== Ensuring WIF provider: ${PROVIDER_ID} ==="
if [ "${PROVIDER_STATE}" = "ACTIVE" ]; then
  echo "Provider already exists and active. Skipping."
elif [ "${PROVIDER_STATE}" = "DISABLED" ]; then
  echo "Provider exists but is disabled. Enabling..."
  gcloud iam workload-identity-pools providers enable "${PROVIDER_ID}" \
    --project="${PROJECT_ID}" --location="global" \
    --workload-identity-pool="${POOL_ID}"
elif [ "${PROVIDER_STATE}" = "DELETED" ]; then
  echo "ERROR: Provider was soft-deleted. Must wait 30 days or use a different name."
  exit 1
else
  echo "Creating provider..."
  gcloud iam workload-identity-pools providers create-oidc "${PROVIDER_ID}" \
    --project="${PROJECT_ID}" \
    --location="global" \
    --workload-identity-pool="${POOL_ID}" \
    --display-name="EduPulse GitHub Actions Provider" \
    --description="WIF provider for EduPulse GitHub Actions" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.owner=assertion.repository_owner,attribute.aud=assertion.aud" \
    --attribute-condition="assertion.repository == '${GITHUB_REPO}'"
  echo "Provider created."
fi

# --- SA bindings ---
POOL_NAME=$(gcloud iam workload-identity-pools describe "${POOL_ID}" \
  --project="${PROJECT_ID}" --location="global" \
  --format="value(name)" 2>/dev/null)
POOL_NUMBER=$(echo "${POOL_NAME}" | sed 's|.*/||' | grep -oE '[0-9]+' | head -1)

# Fallback: extract from full path
if [ -z "${POOL_NUMBER}" ]; then
  POOL_NUMBER=$(echo "${POOL_NAME}" | awk -F'/' '{for(i=1;i<=NF;i++) if($i ~ /^[0-9]+$/) print $i; exit}')
fi

if [ -z "${POOL_NUMBER}" ]; then
  echo "ERROR: Could not determine pool number from: ${POOL_NAME}"
  exit 1
fi

echo ""
echo "=== Granting SA token creator on itself ==="
gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --project="${PROJECT_ID}" \
  --role="roles/iam.serviceAccountTokenCreator" \
  --member="serviceAccount:${SA_EMAIL}" \
  --quiet 2>/dev/null || echo "  Binding may already exist (continuing)"

echo ""
echo "=== Granting WIF impersonation ==="
gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --project="${PROJECT_ID}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${POOL_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/attribute.repository/${GITHUB_REPO}" \
  --quiet 2>/dev/null || echo "  Binding may already exist (continuing)"

echo ""
echo "============================================"
echo "  WIF Setup Complete!"
echo "============================================"
echo ""
echo "Add this to GitHub Secret GCP_WIF_PROVIDER:"
echo "  projects/${POOL_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/providers/${PROVIDER_ID}"
