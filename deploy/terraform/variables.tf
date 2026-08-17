variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud Region"
  type        = string
  default     = "us-east1"
}

variable "environment" {
  description = "Deployment environment (development, staging, production)"
  type        = string
  default     = "development"
}

variable "repository_name" {
  description = "Artifact Registry repository name"
  type        = string
  default     = "edupulse"
}

variable "service_account_name" {
  description = "Name of the service account"
  type        = string
  default     = "edupulse-agent"
}

variable "github_repo" {
  description = "GitHub repository (owner/repo)"
  type        = string
}

variable "wif_pool_id" {
  description = "Workload Identity Federation pool ID (created by deploy/init-wif.sh)"
  type        = string
  default     = "edupulse-gh-actions"
}

variable "dataset_student" {
  description = "BigQuery dataset for student data"
  type        = string
  default     = "edupulse_student_data"
}

variable "dataset_analytics" {
  description = "BigQuery dataset for institutional analytics"
  type        = string
  default     = "edupulse_analytics"
}

variable "model_armor_template_id" {
  description = "Model Armor template ID"
  type        = string
  default     = "edupulse-model-armor-template"
}
