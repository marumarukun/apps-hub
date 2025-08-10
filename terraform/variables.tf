# Terraform Variables for Apps Hub Infrastructure
# These variables are used to customize the infrastructure deployment

variable "project_id" {
  description = "The Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "The Google Cloud region for resources"
  type        = string
  default     = "asia-northeast1"
}

variable "app_name" {
  description = "The name of the application (Cloud Run service name)"
  type        = string
}

variable "allowed_ip_addresses" {
  description = "List of IP addresses/CIDR blocks allowed to access the application"
  type        = list(string)
  default     = []
  
  validation {
    condition     = length(var.allowed_ip_addresses) > 0
    error_message = "At least one IP address must be specified."
  }
}