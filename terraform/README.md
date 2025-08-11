# Terraform Infrastructure for Apps Hub

This directory contains Terraform configurations for managing Apps Hub infrastructure with a **two-level architecture**.

## 📁 Directory Structure

```
terraform/
├── shared/                # Shared resources across all applications
│   ├── main.tf           # Security Policy, IP restrictions
│   ├── variables.tf      # Shared infrastructure variables
│   ├── outputs.tf        # Shared infrastructure outputs
│   └── terraform.tfvars  # IP address configuration (EDIT THIS)
├── app-infrastructure/    # App-specific resources template
│   ├── main.tf           # Load Balancer, NEG, Static IP per app
│   ├── variables.tf      # App infrastructure variables
│   └── outputs.tf        # App infrastructure outputs
└── README.md             # This file
```

## 🔧 For Developers

### 🎯 Changing IP Addresses (Most Common Task)

1. **Edit `terraform/shared/terraform.tfvars`:**
```hcl
allowed_ip_addresses = [
  "160.249.3.131",        # Your current IP
  "160.249.16.211",       # Additional IP
  "203.0.113.0/24"        # CIDR block
]
```

2. **Commit changes:**
```bash
git add terraform/shared/terraform.tfvars
git commit -m "Update allowed IP addresses"
git push origin main
```

3. **Run infrastructure workflow:**
   - Go to GitHub Actions
   - Select "Update Shared Infrastructure"
   - Click "Run workflow"
   - **Done!** All apps now use new IP restrictions

### IP Address Formats

- **Single IP**: `"203.0.113.5"`
- **CIDR Block**: `"192.168.1.0/24"` (range: 192.168.1.0 - 192.168.1.255)
- **IPv6**: `"2001:db8::/32"`

## 🏗️ Architecture Overview

### Two-Level Infrastructure System

#### 1. **Shared Infrastructure** (`shared/`)
- **Purpose**: Resources used by ALL applications
- **Resources**: Security Policy with IP restrictions
- **Workflow**: `infrastructure.yml` (run once for IP changes)
- **State**: `gs://PROJECT_ID-terraform-state/apps-hub/shared/`

#### 2. **App Infrastructure** (`app-infrastructure/`)
- **Purpose**: Resources specific to each individual application
- **Resources**: Load Balancer, NEG, Static IP Address
- **Workflow**: Each app's deployment workflow
- **State**: `gs://PROJECT_ID-terraform-state/apps-hub/app/{app-name}/`

### Benefits of This Design

✅ **One-Click IP Updates**: Change IPs once, apply to all apps  
✅ **Independent Deployments**: Apps don't interfere with each other  
✅ **Persistent State**: No more 409 conflicts from lost Terraform state  
✅ **Static IP Addresses**: No more ephemeral IP changes  
✅ **Clear Separation**: Shared vs app-specific resources  

## 🎯 Managed Resources

### Shared Resources (`shared/`)
- **Cloud Armor Security Policy** (`apps-hub-ip-policy`)
- **IP restriction rules**

### Per-App Resources (`app-infrastructure/`)
- **Static IP Address** (Load Balancer IP)
- **Network Endpoint Group** (NEG)
- **Backend Service** (references shared Security Policy)
- **URL Map**
- **HTTP Target Proxy**
- **Global Forwarding Rule**

## 🔄 Workflows

### IP Address Changes
1. Edit `terraform/shared/terraform.tfvars`
2. Run `infrastructure.yml` workflow **once**
3. All apps immediately use new IP restrictions

### New App Deployment
1. Create app from template
2. Create app-specific workflow
3. Run app's deployment workflow
4. App automatically uses shared IP restrictions

## 🚫 What NOT to Edit

- Infrastructure `.tf` files (managed automatically)
- Only edit `terraform/shared/terraform.tfvars` for IP changes
- State files are managed automatically via GCS backend