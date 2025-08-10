# Terraform Outputs for Apps Hub Infrastructure
# These values are displayed after successful deployment

output "load_balancer_ip" {
  description = "The external IP address of the Load Balancer"
  value       = google_compute_global_forwarding_rule.app_forwarding_rule.ip_address
}

output "app_url" {
  description = "The HTTP URL to access the application"
  value       = "http://${google_compute_global_forwarding_rule.app_forwarding_rule.ip_address}"
}

output "security_policy_name" {
  description = "The name of the Cloud Armor security policy"
  value       = google_compute_security_policy.apps_hub_ip_policy.name
}

output "allowed_ip_addresses" {
  description = "List of allowed IP addresses"
  value       = var.allowed_ip_addresses
}