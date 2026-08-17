# EduPulse Clean Setup Guide

## Prerequisites

1. **GCP Account**: Your GCP account with billing enabled
2. **Project**: Your GCP project ID
3. **GitHub Repo**: Your fork of `EduPulse-Student-Success-AI` (set `GITHUB_REPO` to `<your-org>/EduPulse-Student-Success-AI` in `.env`)
4. **Gemini API Key**: From https://aistudio.google.com/api-keys
5. **AgentOps API Key**: From https://app.agentops.ai (optional — enables session replays and agent analytics)

---

## Step 1: Enable GCP APIs

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable bigquery.googleapis.com firestore.googleapis.com run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com iam.googleapis.com aiplatform.googleapis.com secretmanager.googleapis.com compute.googleapis.com cloudtrace.googleapis.com monitoring.googleapis.com modelarmor.googleapis.com
```

---

## Step 2: Create Workload Identity Federation

```bash
bash deploy/init-wif.sh
```

Copy the output and save it — you'll need it for GitHub Secrets.

> If you created the pool/provider with a custom name (e.g.
> `POOL_ID=my-pool PROVIDER_ID=my-provider bash deploy/init-wif.sh`), set the
> matching `WIF_POOL_ID` / `WIF_PROVIDER_ID` **repo variables** in Step 3, or CI
> will fall back to the default names.

---

## Step 3: Set GitHub Secrets

Go to: **GitHub repo → Settings → Secrets and variables → Actions**

| Secret | Value |
|--------|-------|
| `GCP_PROJECT_ID` | Your GCP project ID |
| `GCP_WIF_PROVIDER` | Output from Step 2 |
| `GEMINI_API_KEY` | Your Gemini API key |
| `AGENTOPS_API_KEY` | Your AgentOps API key (from https://app.agentops.ai) |

### Repository Variables (Optional)

Set these as **Variables** (same page, **Actions → Variables** tab), not Secrets.
Only set the ones that differ from the defaults:

| Variable | Value | Default |
|----------|-------|---------|
| `WIF_POOL_ID` | WIF pool ID created in Step 2 (e.g. `your-named-edupulse-gh-actions`) | `edupulse-gh-actions` |
| `WIF_PROVIDER_ID` | WIF provider ID created in Step 2 (e.g. `your-named-edupulse-oidc-provider`) | `edupulse-oidc-provider` |
| `REGION` | GCP region | `us-east1` |
| `SERVICE_NAME` | Cloud Run service name | `edupulse-agent` |
| `REPOSITORY_NAME` | Artifact Registry repository | `edupulse` |
| `MODEL_ARMOR_TEMPLATE_ID` | Model Armor template ID | `edupulse-model-armor-template` |
| `DATASET_STUDENT` | BigQuery student-data dataset | `edupulse_student_data` |
| `DATASET_ANALYTICS` | BigQuery analytics dataset | `edupulse_analytics` |
| `TERRAFORM_VERSION` | Terraform version for CI | `1.15.8` |

> **Important**: `WIF_POOL_ID` / `WIF_PROVIDER_ID` are **required** whenever your
> pool or provider was created with a name other than the default — e.g. the
> default `edupulse-gh-actions` was soft-deleted and you recreated it under a
> new name. Without them, CI falls back to the default names and `terraform apply`
> fails with `Identity Pool does not exist`.
>
> A **soft-deleted** WIF pool keeps its name locked in a hidden, inactive state for
> **30 days** before GCP permanently purges it, so you cannot reuse the original
> pool name during that window. Recreate the pool under a new name (e.g.
> `edupulse-gh-actions-2`) and set `WIF_POOL_ID` to match. Only the pool name is
> locked — the provider name is not, so `WIF_PROVIDER_ID` can keep its value.

---

## Step 4: Create Terraform Resources

```bash
cd deploy/terraform
terraform init
terraform apply
```

---

## Step 5: Seed Data

```bash
python deploy/initial/seed_bigquery.py
python deploy/initial/seed_firestore.py
```

---

## Step 6: Deploy

```bash
git add . && git commit -m "Initial deploy" && git push
```

CI/CD will:
1. Create/update GCP resources
2. Build Docker image
3. Deploy to Cloud Run

---

## Verify

```bash
# Check Cloud Run
gcloud run services describe "${SERVICE_NAME:-edupulse-agent}" --region="${REGION:-us-east1}" --format="value(status.url)"
```

Open the URL in browser to access ADK Dev UI.

---

## What Each Component Does

| Component | Purpose |
|-----------|---------|
| Terraform | Creates datasets, SA, IAM, APIs, Model Armor template |
| seed_bigquery.py | Creates tables and loads data |
| seed_firestore.py | Loads Firestore collections |
| CI/CD | Builds Docker, deploys to Cloud Run with Model Armor env vars |

---

## Cleanup

```bash
cd deploy/terraform
terraform destroy

rm -f deploy/terraform/terraform.tfstate deploy/terraform/terraform.tfstate.backup
```

```bash
cd ../../
bash deploy/cleanup.sh
# This will DELETE all EduPulse resources. Continue? (yes/no): yes
# Also delete Workload Identity Federation pool and provider? [y/N]: N (keep it — no need to re-create again!)
# Delete Firestore data (4 collections)? [y/N]: y
```

> **NOTE - Workload Identity Federation (WIF):**
>
> - **`N` (recommended)** - Keep the WIF pool and provider. Use this if you want
>   to re-run the setup later (re-deploy via GitHub Actions, run `init-wif.sh`,
>   or do a fresh `terraform apply`). The CI/CD workflow and `init-wif.sh` expect
>   the pool/provider to already exist, so keeping them lets you stand up the
>   project again without recreating WIF.
> - **`y`** - Delete the WIF pool and provider. Use this ONLY for a complete
>   teardown when you no longer plan to use EduPulse. Only the **pool** is
>   **soft-deleted for ~30 days** and cannot be recreated under the same name
>   until that period ends; the **provider** name is NOT locked and can be reused
>   immediately. To set up again afterward, run `init-wif.sh` with a
>   new `POOL_ID` only (e.g. `your-named-edupulse-gh-actions`) and set the matching
>   `WIF_POOL_ID` repo variable. `PROVIDER_ID` / `WIF_PROVIDER_ID` can keep the
>   same value.

---

## Troubleshooting

**403 Permission Denied**: Run `init-wif.sh` again

**403 modelarmor.templates.create**: SA needs `roles/modelarmor.admin` (Terraform handles this)

**409 Already Exists**: Import the resource first

**429 Rate Limited**: Wait 25 seconds and retry

**Tables Empty**: Run `seed_bigquery.py` again
