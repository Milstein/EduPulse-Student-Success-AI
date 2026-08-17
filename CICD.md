# EduPulse CI/CD Pipeline

## Overview

Automated pipeline for testing, building, and deploying the EduPulse multi-agent system to GCP Cloud Run.

**Trigger**: Push to `main` branch

---

## Pipeline Structure

```
test ──► ensure-infra ──► build ──► deploy
```

---

## Jobs

### 1. ensure-infra

Ensures GCP infrastructure exists via Terraform.

| Step | Description |
|------|-------------|
| Checkout code | Clone repository |
| Authenticate to GCP | WIF auth to GCP |
| Setup Terraform | Install Terraform (default `1.15.8`, override via `TERRAFORM_VERSION` variable) |
| Grant required roles to SA | Add bigquery.admin, iam.serviceAccountAdmin to deploy SA |
| Initialize Terraform | `terraform init` |
| Import existing resources | Import existing AR, SA, BQ datasets, Model Armor template |
| Run terraform plan | Preview infrastructure changes |
| Run terraform apply | Apply changes (main branch only) |

**Resources managed**: Artifact Registry, Service Account + IAM, BigQuery datasets, Model Armor template

---

### 2. test

Runs linting and eval tests.

| Step | Description |
|------|-------------|
| Checkout code | Clone repository |
| Setup Python | Python 3.11 |
| Install dependencies | pip install requirements.txt, pytest, ruff |
| Lint | `ruff check edupulse/ tools/` |
| Run evals | `pytest tests/ -v --tb=short` |

**Tests cover**: Agent structure (routing, tool usage, FERPA compliance, data isolation) in `test_agents.py`; Tool data accuracy and intervention quality in `test_tools.py`; Model Armor guard behavior (wiring, block/allow, fail-open) in `test_model_armor.py`

---

### 3. build

Builds and pushes Docker image to Artifact Registry.

| Step | Description |
|------|-------------|
| Checkout code | Clone repository |
| Authenticate to GCP | WIF auth to GCP |
| Setup gcloud CLI | Install gcloud |
| Configure Docker auth | Auth for Artifact Registry |
| Build and push Docker image | Build, tag with SHA + latest, push |

**Image**: `$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$SERVICE_NAME:{sha}`

---

### 4. deploy

Deploys to Cloud Run.

| Step | Description |
|------|-------------|
| Checkout code | Clone repository |
| Authenticate to GCP | WIF auth to GCP |
| Setup gcloud CLI | Install gcloud |
| Deploy to Cloud Run | Deploy with env vars (incl. Model Armor), memory, scaling |
| Get service URL | Output the service URL |

**Service**: `$SERVICE_NAME` (default `edupulse-agent`) at `https://$SERVICE_NAME-*.a.run.app`

**Cloud Run Configuration**:
- Memory: 4 GiB
- CPU: 2 vCPU
- Min instances: 0 (scales to zero)
- Max instances: 10
- Concurrency: 80 requests per instance
- Request timeout: 300 seconds
- Auth: `--allow-unauthenticated`

---

## Dependencies

```
test ──► ensure-infra ──► build ──► deploy
```

- `ensure-infra` depends on `test`
- `build` depends on `ensure-infra`
- `deploy` depends on `build`

---

## Secrets Required

| Secret | Description |
|--------|-------------|
| `GCP_PROJECT_ID` | GCP project ID |
| `GCP_WIF_PROVIDER` | Workload Identity Federation provider |
| `GEMINI_API_KEY` | Gemini API key |
| `AGENTOPS_API_KEY` | AgentOps API key for observability |

> **Note**: Model Armor env vars (`MODEL_ARMOR_PROJECT_ID`, `MODEL_ARMOR_LOCATION`, `MODEL_ARMOR_TEMPLATE_ID`) are derived from repo variables/secrets — no GitHub secrets needed.

---

## Environment Variables

| Variable | Value |
|----------|-------|
| `PROJECT_ID` | `${{ secrets.GCP_PROJECT_ID }}` |
| `REGION` | `${{ vars.REGION || 'us-east1' }}` |
| `SERVICE_NAME` | `${{ vars.SERVICE_NAME || 'edupulse-agent' }}` |
| `REPOSITORY_NAME` | `${{ vars.REPOSITORY_NAME || 'edupulse' }}` |
| `MODEL_ARMOR_TEMPLATE_ID` | `${{ vars.MODEL_ARMOR_TEMPLATE_ID || 'edupulse-model-armor-template' }}` |
| `TERRAFORM_VERSION` | `${{ vars.TERRAFORM_VERSION || '1.15.8' }}` |
| `TF_VAR_project_id` | `${{ secrets.GCP_PROJECT_ID }}` |
| `TF_VAR_github_repo` | `${{ github.repository }}` |
| `TF_VAR_wif_pool_id` | `${{ vars.WIF_POOL_ID || 'edupulse-gh-actions' }}` |
| `IMAGE_REPO` | `$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$SERVICE_NAME` |

---

## Running Manually

### Deploy from local

```bash
export PROJECT_ID=YOUR_PROJECT_ID
export REGION=us-east1
export SERVICE_NAME=edupulse-agent
export REPOSITORY_NAME=edupulse
export GITHUB_REPO=owner/your-repo
export MODEL_ARMOR_TEMPLATE_ID=edupulse-model-armor-template

# 1. Ensure infra
cd deploy/terraform
terraform init
terraform apply -var="project_id=$PROJECT_ID" -var="github_repo=$GITHUB_REPO"

# 2. Build image
gcloud builds submit --config=deploy/cloudbuild.yaml . --project="$PROJECT_ID" \
  --substitutions=_REGION="$REGION",_REPOSITORY="$REPOSITORY_NAME",_SERVICE="$SERVICE_NAME"

# 3. Deploy to Cloud Run (with env vars matching CI/CD pipeline)
gcloud run deploy "$SERVICE_NAME" \
  --image="$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$SERVICE_NAME:latest" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --allow-unauthenticated \
  --set-env-vars="PROJECT_ID=$PROJECT_ID,GEMINI_API_KEY=$GEMINI_API_KEY,AGENTOPS_API_KEY=$AGENTOPS_API_KEY,MODEL_ARMOR_PROJECT_ID=$PROJECT_ID,MODEL_ARMOR_LOCATION=$REGION,MODEL_ARMOR_TEMPLATE_ID=$MODEL_ARMOR_TEMPLATE_ID"
```

### Run tests locally

```bash
pytest tests/ -v --tb=short
```

### Run eval tests locally

```bash
pytest eval/ -v
```
