terraform {
  required_version = ">= 1.15"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.40"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

data "google_project" "project" {
  project_id = var.project_id
}

# ============================================================
# APIs
# ============================================================

resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "bigquery.googleapis.com",
    "aiplatform.googleapis.com",
    "secretmanager.googleapis.com",
    "compute.googleapis.com",
    "firestore.googleapis.com",
    "cloudtrace.googleapis.com",
    "monitoring.googleapis.com",
    "modelarmor.googleapis.com",
  ])

  project = var.project_id
  service = each.key

  disable_on_destroy = false
}

# ============================================================
# Artifact Registry
# ============================================================

resource "google_artifact_registry_repository" "edupulse" {
  location      = var.region
  repository_id = var.repository_name
  description   = "Docker images for EduPulse agent"
  format        = "DOCKER"

  labels = {
    environment = var.environment
    application = var.repository_name
  }

  depends_on = [google_project_service.apis]
}

# ============================================================
# Service Account
# ============================================================

resource "google_service_account" "edupulse" {
  account_id   = var.service_account_name
  display_name = "EduPulse Agent Service Account"
  description  = "Service account for EduPulse agent on Cloud Run"
}

resource "google_project_iam_member" "edupulse_roles" {
  for_each = toset([
    "roles/run.admin",
    "roles/run.developer",
    "roles/run.invoker",
    "roles/artifactregistry.writer",
    "roles/artifactregistry.reader",
    "roles/bigquery.dataViewer",
    "roles/bigquery.jobUser",
    "roles/bigquery.dataEditor",
    "roles/aiplatform.user",
    "roles/aiplatform.serviceAgent",
    "roles/ml.admin",
    "roles/secretmanager.secretAccessor",
    "roles/secretmanager.admin",
    "roles/storage.admin",
    "roles/cloudbuild.builds.builder",
    "roles/logging.logWriter",
    "roles/cloudtrace.agent",
    "roles/monitoring.metricWriter",
    "roles/iam.serviceAccountUser",
    "roles/iam.serviceAccountTokenCreator",
    "roles/datastore.owner",
    "roles/discoveryengine.admin",
    "roles/resourcemanager.projectIamAdmin",
    "roles/modelarmor.admin",
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.edupulse.email}"
}

# Allow SA to get its own access token (required for WIF auth to work)
resource "google_service_account_iam_member" "self_token_creator" {
  service_account_id = google_service_account.edupulse.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${google_service_account.edupulse.email}"
}

# Re-associate WIF impersonation when SA is recreated
# WIF pool/provider are managed outside Terraform (init-wif.sh)

resource "google_service_account_iam_member" "wif_impersonation" {
  service_account_id = google_service_account.edupulse.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/projects/${data.google_project.project.number}/locations/global/workloadIdentityPools/${var.wif_pool_id}/attribute.repository/${var.github_repo}"

  depends_on = [google_service_account.edupulse]
}

# ============================================================
# Cloud Run - Deployed by GitHub Actions (not Terraform)
# because the Docker image must be built first.
# ============================================================

# ============================================================
# BigQuery - Student Data
# ============================================================

resource "google_bigquery_dataset" "student_data" {
  dataset_id                 = var.dataset_student
  friendly_name              = "EduPulse Student Data"
  description                = "Student records, courses, enrollments, and academic data"
  location                   = var.region
  delete_contents_on_destroy = true

  labels = {
    environment = var.environment
    application = var.repository_name
  }

  depends_on = [google_project_service.apis]
}

# ============================================================
# BigQuery - Analytics
# ============================================================

resource "google_bigquery_dataset" "analytics" {
  dataset_id                 = var.dataset_analytics
  friendly_name              = "EduPulse Analytics"
  description                = "Institutional analytics, retention trends, and department comparisons"
  location                   = var.region
  delete_contents_on_destroy = true

  labels = {
    environment = var.environment
    application = var.repository_name
  }

  depends_on = [google_project_service.apis]
}

# ============================================================
# Model Armor - LLM Security Template
# ============================================================

resource "google_model_armor_template" "edupulse" {
  template_id = var.model_armor_template_id
  location    = var.region
  project     = var.project_id

  filter_config {
    pi_and_jailbreak_filter_settings {
      filter_enforcement = "ENABLED"
      confidence_level   = "HIGH"
    }

    rai_settings {
      rai_filters {
        filter_type      = "HATE_SPEECH"
        confidence_level = "HIGH"
      }
      rai_filters {
        filter_type      = "HARASSMENT"
        confidence_level = "MEDIUM_AND_ABOVE"
      }
      rai_filters {
        filter_type      = "SEXUALLY_EXPLICIT"
        confidence_level = "HIGH"
      }
      rai_filters {
        filter_type      = "DANGEROUS"
        confidence_level = "HIGH"
      }
    }

    sdp_settings {
      basic_config {
        filter_enforcement = "ENABLED"
      }
    }

    malicious_uri_filter_settings {
      filter_enforcement = "ENABLED"
    }
  }

  template_metadata {
    log_template_operations = true
    log_sanitize_operations = true
  }

  labels = {
    environment = var.environment
    application = var.repository_name
  }

  depends_on = [google_project_service.apis, google_project_iam_member.edupulse_roles]
}

# BigQuery tables are NOT managed by Terraform.
# Tables are created and seeded by deploy/initial/seed_bigquery.py
# This avoids deletion_protection conflicts on CI/CD runs.

# Firestore (default) database is NOT managed by Terraform.
# GCP doesn't allow deletion of the default database.
# Data cleanup is handled by deploy/cleanup.sh (clears all collections).
