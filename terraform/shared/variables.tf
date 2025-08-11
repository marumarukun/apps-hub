# Variables for Apps Hub Shared Infrastructure

variable "project_id" {
  description = "The Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "The Google Cloud region for resources"
  type        = string
  default     = "asia-northeast1"
}

variable "allowed_ip_addresses" {
  description = "List of IP addresses/CIDR blocks allowed to access all applications"
  type        = list(string)
  default     = []
  
  validation {
    condition     = length(var.allowed_ip_addresses) > 0
    error_message = "At least one IP address must be specified."
  }
}