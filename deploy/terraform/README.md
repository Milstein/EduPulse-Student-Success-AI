# EduPulse Terraform Deployment

## Prerequisites

1. [Terraform](https://www.terraform.io/downloads.html) >= 1.15
2. [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud`)
3. GCP Project with billing enabled
4. Docker (for building the container image)

## Quick Start

```bash
cd deploy/terraform

# 1. Copy and edit variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# 2. Initialize Terraform
terraform init

# 3. Review the plan
terraform plan

# 4. Apply (deploy)
terraform apply

# 5. Show outputs
terraform output
```

## What Gets Deployed

| Resource | Description |
|----------|-------------|
| Artifact Registry repo | `var.repository_name` (default `edupulse`) - Docker image storage |
| Service Account | `var.service_account_name` (default `edupulse-agent`) with all required IAM roles |
| IAM bindings | Roles for BigQuery, Gemini Enterprise Agent Platform (formerly Vertex AI), Model Armor, etc. |
| BigQuery datasets | `var.dataset_student`, `var.dataset_analytics` |
| Model Armor template | `var.model_armor_template_id` — LLM security filters (prompt injection, PII, jailbreak, harmful content) |

> **Note**: Cloud Run deployment is handled by GitHub Actions (`deploy.yml`), not Terraform.

## Cleanup (Destroy Everything)

```bash
terraform destroy
```

This removes **all** resources created by Terraform:
- Artifact Registry repository
- Service account and IAM bindings
- BigQuery datasets (`var.dataset_student`, `var.dataset_analytics`)
- Model Armor template (`var.model_armor_template_id`)

## Commands

```bash
# Initialize (first time only)
terraform init

# See what will be created
terraform plan

# Deploy
terraform apply

# Show outputs
terraform output

# Destroy everything
terraform destroy

# Refresh state (check for drift)
terraform plan -refresh-only
```

## Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `project_id` | GCP Project ID | (required) |
| `github_repo` | GitHub repository (owner/repo) | (required) |
| `region` | GCP Region | `us-east1` |
| `environment` | Environment name | `development` |
| `repository_name` | Artifact Registry repository name | `edupulse` |
| `service_account_name` | SA name | `edupulse-agent` |
| `wif_pool_id` | WIF pool ID (created by `deploy/init-wif.sh`) | `edupulse-gh-actions` |
| `dataset_student` | BigQuery student data dataset | `edupulse_student_data` |
| `dataset_analytics` | BigQuery analytics dataset | `edupulse_analytics` |
| `model_armor_template_id` | Model Armor template ID | `edupulse-model-armor-template` |

## Outputs

| Output | Description |
|--------|-------------|
| `service_account_email` | Email of the created service account |
| `artifact_registry_url` | URL of the Artifact Registry repository |
| `model_armor_template_name` | Resource name of the Model Armor template |
