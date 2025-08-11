# Variables for Apps Hub App-Specific Infrastructure

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