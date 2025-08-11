# Outputs for Apps Hub Shared Infrastructure

output "security_policy_id" {
  description = "The ID of the shared Cloud Armor security policy"
  value       = google_compute_security_policy.apps_hub_ip_policy.id
}

output "security_policy_name" {
  description = "The name of the shared Cloud Armor security policy"
  value       = google_compute_security_policy.apps_hub_ip_policy.name
}

output "allowed_ip_addresses" {
  description = "List of allowed IP addresses"
  value       = var.allowed_ip_addresses
}