# Apps Hub Terraform Infrastructure

This directory contains Terraform configuration files for managing Apps Hub infrastructure, including Load Balancer and Cloud Armor IP restrictions.

## 📁 File Structure

```
terraform/
├── main.tf              # Main Terraform resources (Cloud Armor + Load Balancer)
├── variables.tf         # Variable definitions
├── terraform.tfvars     # Configuration values (EDIT THIS FOR IP CHANGES)
├── outputs.tf           # Output values
└── README.md            # This file
```

## 🔧 For Developers

### Changing Allowed IP Addresses

1. **Edit `terraform.tfvars`:**
```hcl
allowed_ip_addresses = [
  "160.249.3.131",        # Your current IP
  "192.168.1.100",        # Additional IP
  "203.0.113.0/24"        # CIDR block
]
```

2. **Commit changes:**
```bash
git add terraform/terraform.tfvars
git commit -m "Update allowed IP addresses"
git push origin main
```

3. **Deploy any app** - Changes will be applied automatically

### IP Address Formats

- **Single IP**: `"203.0.113.5"`
- **CIDR Block**: `"192.168.1.0/24"` (range: 192.168.1.0 - 192.168.1.255)
- **IPv6**: `"2001:db8::/32"`

## 🚫 What NOT to Edit

- `main.tf` - Infrastructure resources (managed by infrastructure team)
- `variables.tf` - Variable definitions (managed by infrastructure team)
- `outputs.tf` - Output definitions (managed by infrastructure team)

## 🔍 Troubleshooting

### Check Current State
```bash
cd terraform
terraform show
```

### View Planned Changes
```bash
cd terraform
terraform plan
```

### Manual Apply (if needed)
```bash
cd terraform
terraform apply
```

## 🎯 Managed Resources

This Terraform configuration manages:

- **Cloud Armor Security Policy** (`apps-hub-ip-policy`)
- **Load Balancer Components:**
  - Network Endpoint Group (NEG)
  - Backend Service
  - URL Map
  - HTTP Target Proxy
  - Global Forwarding Rule

## 🔄 Automatic Management

- **GitHub Actions** automatically runs `terraform apply` during app deployment
- **IP changes** in `terraform.tfvars` are applied on next deployment
- **State management** is handled automatically
- **Resource dependencies** are managed by Terraform