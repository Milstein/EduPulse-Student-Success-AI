#!/bin/bash
# EduPulse Cleanup Script
# Cleans up resources NOT managed by Terraform. Run AFTER `terraform destroy`:
#
#   cd deploy/terraform && terraform destroy
#   bash deploy/cleanup.sh
#
# Terraform destroy already removes: Artifact Registry repo, BigQuery datasets,
# the edupulse-agent SA + its IAM roles/bindings, Model Armor template, APIs.
# This script removes the rest: Cloud Run services, Firestore collections,
# legacy github-actions SA + IAM bindings, and optionally the WIF pool/provider.
#
# Usage:
#   chmod +x deploy/cleanup.sh
#   ./deploy/cleanup.sh

set -e

# Load .env file if it exists
if [ -f "$(dirname "$0")/../.env" ]; then
    export $(grep -v '^#' "$(dirname "$0")/../.env" | xargs)
fi

PROJECT_ID="${PROJECT_ID:?ERROR: PROJECT_ID not set. Add it to .env or export it.}"
REGION="${REGION:-us-east1}"
SERVICE_ACCOUNT_NAME="${SERVICE_ACCOUNT_NAME:-edupulse-agent}"
POOL_ID="${POOL_ID:-edupulse-gh-actions}"
PROVIDER_ID="${PROVIDER_ID:-edupulse-oidc-provider}"
COLLECTION_ENGAGEMENT="${COLLECTION_ENGAGEMENT:-student_engagement}"
COLLECTION_ALERTS="${COLLECTION_ALERTS:-active_alerts}"
COLLECTION_ADVISOR_NOTES="${COLLECTION_ADVISOR_NOTES:-advisor_notes}"
COLLECTION_SESSIONS="${COLLECTION_SESSIONS:-student_sessions}"

echo "============================================"
echo "  EduPulse - GCP Resource Cleanup"
echo "  Project: $PROJECT_ID"
echo "  Region: $REGION"
echo "============================================"
echo ""

# Confirm
read -p "This will DELETE all EduPulse resources. Continue? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

# Ask about WIF (created outside Terraform)
read -p "Also delete Workload Identity Federation pool and provider? [y/N]: " DELETE_WIF
DELETE_WIF="${DELETE_WIF:-N}"

echo ""
echo "--- Deleting Cloud Run services ---"
gcloud run services delete "${SERVICE_ACCOUNT_NAME}" --region=$REGION --project=$PROJECT_ID --quiet 2>/dev/null || echo "  Not found or already deleted"
gcloud run services delete "${SERVICE_ACCOUNT_NAME}-development" --region=$REGION --project=$PROJECT_ID --quiet 2>/dev/null || echo "  Not found or already deleted"

echo ""
echo "--- Deleting Firestore data ---"
read -p "Delete Firestore data (4 collections)? [y/N]: " DELETE_FS
DELETE_FS="${DELETE_FS:-N}"
if [ "$DELETE_FS" = "y" ] || [ "$DELETE_FS" = "yes" ]; then
    python3 -c "
from google.cloud import firestore
client = firestore.Client(project='$PROJECT_ID')
for col in ['${COLLECTION_ENGAGEMENT}', '${COLLECTION_ALERTS}', '${COLLECTION_ADVISOR_NOTES}', '${COLLECTION_SESSIONS}']:
    docs = client.collection(col).stream()
    for doc in docs:
        doc.reference.delete()
    print(f'  Cleared collection: {col}')
" 2>/dev/null || echo "  Firestore not available or already empty"
else
    echo "  Skipping Firestore data"
fi

echo ""
echo "--- Removing project-level IAM bindings for legacy github-actions SA ---"
SA="github-actions@${PROJECT_ID}.iam.gserviceaccount.com"
echo "  Cleaning bindings for: $SA"
BINDINGS=$(gcloud projects get-iam-policy $PROJECT_ID --format="json(bindings)" 2>/dev/null | python3 -c "
import json, sys
data = json.load(sys.stdin)
for b in data.get('bindings', []):
    if '$SA' in b.get('members', []):
        print(b['role'])
" 2>/dev/null || true)
for ROLE in $BINDINGS; do
    gcloud projects remove-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA" --role="$ROLE" --quiet 2>/dev/null || true
done
echo "  All IAM bindings cleaned"

echo ""
echo "--- Deleting legacy github-actions service account ---"
gcloud iam service-accounts delete github-actions@${PROJECT_ID}.iam.gserviceaccount.com --project=$PROJECT_ID --quiet 2>/dev/null || echo "  Not found or already deleted"

if [ "$DELETE_WIF" = "y" ] || [ "$DELETE_WIF" = "yes" ]; then
    echo ""
    echo "--- Deleting Workload Identity Federation ---"
    gcloud iam workload-identity-pools providers delete ${PROVIDER_ID} \
      --project=$PROJECT_ID --location=global \
      --workload-identity-pool=${POOL_ID} --quiet 2>/dev/null || echo "  Provider not found or already deleted"
    gcloud iam workload-identity-pools delete ${POOL_ID} \
      --project=$PROJECT_ID --location=global --quiet 2>/dev/null || echo "  Pool not found or already deleted"
else
    echo ""
    echo "--- Skipping WIF (preserved) ---"
fi

echo ""
echo "============================================"
echo "  Cleanup complete!"
echo "============================================"
