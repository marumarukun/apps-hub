# Outputs for Apps Hub App-Specific Infrastructure

output "load_balancer_ip" {
  description = "The external IP address of the Load Balancer"
  value       = google_compute_global_address.app_lb_ip.address
}

output "app_url" {
  description = "The HTTP URL to access the application"
  value       = "http://${google_compute_global_address.app_lb_ip.address}"
}

output "backend_service_name" {
  description = "The name of the backend service"
  value       = google_compute_backend_service.app_backend.name
}

output "security_policy_attached" {
  description = "The attached security policy name"
  value       = data.google_compute_security_policy.shared_ip_policy.name
}