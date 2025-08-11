# Apps Hub Shared Infrastructure Configuration
# This file manages IP restrictions for ALL applications

# IP addresses allowed to access applications
# Add or remove IP addresses as needed
# Supports both single IPs (203.0.113.5) and CIDR blocks (192.168.1.0/24)
allowed_ip_addresses = [
  "160.249.3.131",
  "160.249.16.211",
  # Add your IP addresses here:
  # "192.168.1.100",
  # "203.0.113.0/24"
]

# Note: project_id is automatically set by GitHub Actions
# You don't need to modify it here