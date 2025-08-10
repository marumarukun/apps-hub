#!/bin/bash

# Cloud Armor Policy Management Script for Apps Hub
# This script manages IP restriction rules for the shared Cloud Armor policy

set -euo pipefail

# Configuration
POLICY_NAME="apps-hub-ip-policy"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if policy exists
check_policy_exists() {
    if gcloud compute security-policies describe "${POLICY_NAME}" --quiet >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to update IP allow rules
update_ip_rules() {
    local allowed_ips="$1"
    
    if [[ -z "${allowed_ips}" ]]; then
        log_error "No IP addresses provided"
        exit 1
    fi

    log_info "Updating IP rules for policy: ${POLICY_NAME}"
    
    # Delete existing allow rules (priority 1000-1999 are reserved for IP allow rules)
    log_info "Removing existing IP allow rules..."
    
    # Simple approach: just try to delete known priority ranges
    log_info "Attempting to delete any existing IP allow rules (priorities 1000-1999)..."
    
    for priority in {1000..1010}; do
        log_info "Attempting to delete rule with priority ${priority}..."
        gcloud compute security-policies rules delete "${priority}" \
            --security-policy="${POLICY_NAME}" \
            --quiet 2>/dev/null && log_info "Deleted rule ${priority}" || log_info "Rule ${priority} not found (OK)"
    done
    
    # Wait for deletions to complete
    sleep 5
    
    log_info "Cleanup completed"
    
    # Add new IP allow rules
    log_info "Adding new IP allow rules..."
    
    IFS=',' read -ra IP_ARRAY <<< "${allowed_ips}"
    priority=1000
    
    for ip in "${IP_ARRAY[@]}"; do
        # Trim whitespace
        ip=$(echo "${ip}" | xargs)
        
        if [[ -z "${ip}" ]]; then
            continue
        fi
        
        # Validate IP format (basic validation)
        if [[ "${ip}" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(/[0-9]+)?$ ]]; then
            log_info "Adding allow rule for IP: ${ip} (priority: ${priority})"
            
            gcloud compute security-policies rules create "${priority}" \
                --security-policy="${POLICY_NAME}" \
                --src-ip-ranges="${ip}" \
                --action="allow" \
                --description="Allow access from ${ip}" \
                --quiet
            
            ((priority++))
        else
            log_error "Invalid IP format: ${ip}"
            exit 1
        fi
    done
    
    log_info "IP rules updated successfully"
}

# Function to display current policy status
show_policy_status() {
    log_info "Current Cloud Armor policy status:"
    echo "Policy Name: ${POLICY_NAME}"
    
    if check_policy_exists; then
        echo "Status: EXISTS"
        echo ""
        echo "Current Rules:"
        gcloud compute security-policies rules list \
            --security-policy="${POLICY_NAME}" \
            --format="table(priority,action,srcIpRanges.list():label=SOURCE_IPS,description)"
    else
        echo "Status: NOT_FOUND"
        log_error "Policy ${POLICY_NAME} does not exist"
        exit 1
    fi
}

# Main function
main() {
    local command="${1:-status}"
    
    case "${command}" in
        "update")
            local allowed_ips="${2:-}"
            if [[ -z "${allowed_ips}" ]]; then
                log_error "Usage: $0 update <comma_separated_ip_list>"
                exit 1
            fi
            update_ip_rules "${allowed_ips}"
            ;;
        "status")
            show_policy_status
            ;;
        *)
            echo "Usage: $0 {update|status}"
            echo "  update <ip_list>  - Update IP allow rules"
            echo "  status            - Show current policy status"
            exit 1
            ;;
    esac
}

# Execute main function with all arguments
main "$@"