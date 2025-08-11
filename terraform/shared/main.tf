# Apps Hub Shared Infrastructure
# This manages resources shared across all applications

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  # Store shared Terraform state in Google Cloud Storage
  backend "gcs" {
    bucket = "PROJECT_ID-terraform-state"
    prefix = "apps-hub/shared"
  }
}

# Configure the Google Cloud Provider
provider "google" {
  project = var.project_id
  region  = var.region
}

# Cloud Armor Security Policy for IP Restriction (Shared across all apps)
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