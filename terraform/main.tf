# Apps Hub Terraform Configuration
# This file manages Load Balancer and Cloud Armor resources for IP restriction

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# Configure the Google Cloud Provider
provider "google" {
  project = var.project_id
  region  = var.region
}

# Cloud Armor Security Policy for IP Restriction
resource "google_compute_security_policy" "apps_hub_ip_policy" {
  name        = "apps-hub-ip-policy"
  description = "IP restriction policy for Apps Hub applications"

  # Allow rules for specified IP addresses
  dynamic "rule" {
    for_each = var.allowed_ip_addresses
    content {
      action   = "allow"
      priority = 1000 + rule.key
      description = "Allow access from ${rule.value}"
      
      match {
        config {
          src_ip_ranges = [rule.value]
        }
        versioned_expr = "SRC_IPS_V1"
      }
    }
  }

  # Default deny rule
  rule {
    action   = "deny(403)"
    priority = 2147483647
    description = "Default deny rule"
    
    match {
      config {
        src_ip_ranges = ["*"]
      }
      versioned_expr = "SRC_IPS_V1"
    }
  }
}

# Data source to get Cloud Run service information
# Note: The Cloud Run service must exist before running Terraform
data "google_cloud_run_service" "app" {
  name     = var.app_name
  location = var.region
}

# Network Endpoint Group for Cloud Run
resource "google_compute_region_network_endpoint_group" "cloud_run_neg" {
  name                  = "${var.app_name}-neg"
  region                = var.region
  network_endpoint_type = "SERVERLESS"

  cloud_run {
    service = data.google_cloud_run_service.app.name
  }

  depends_on = [data.google_cloud_run_service.app]
}

# Backend Service
resource "google_compute_backend_service" "app_backend" {
  name                  = "${var.app_name}-backend"
  protocol              = "HTTP"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  timeout_sec           = 30
  
  backend {
    group = google_compute_region_network_endpoint_group.cloud_run_neg.id
  }

  # Attach the security policy
  security_policy = google_compute_security_policy.apps_hub_ip_policy.id
}

# URL Map
resource "google_compute_url_map" "app_url_map" {
  name            = "${var.app_name}-url-map"
  default_service = google_compute_backend_service.app_backend.id
}

# HTTP Target Proxy
resource "google_compute_target_http_proxy" "app_target_proxy" {
  name    = "${var.app_name}-proxy"
  url_map = google_compute_url_map.app_url_map.id
}

# Global Forwarding Rule
resource "google_compute_global_forwarding_rule" "app_forwarding_rule" {
  name                  = "${var.app_name}-forwarding-rule"
  target                = google_compute_target_http_proxy.app_target_proxy.id
  port_range           = "80"
  load_balancing_scheme = "EXTERNAL_MANAGED"
}