output "service_account_email" {
  description = "Email of the service account"
  value       = google_service_account.edupulse.email
}

output "artifact_registry_url" {
  description = "URL of the Artifact Registry repository"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}"
}

output "model_armor_template_name" {
  description = "Resource name of the Model Armor template"
  value       = google_model_armor_template.edupulse.name
}
