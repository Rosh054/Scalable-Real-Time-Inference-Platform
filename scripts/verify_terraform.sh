#!/usr/bin/env bash
# Validates Terraform without AWS spend (no terraform apply).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/terraform"

echo "=== Terraform validation (no AWS apply) ==="

command -v terraform >/dev/null || { echo "Install: brew tap hashicorp/tap && brew install hashicorp/tap/terraform"; exit 1; }

terraform fmt -check -recursive || { echo "Run: terraform fmt -recursive"; exit 1; }
echo "PASS: terraform fmt"

terraform init -backend=false -input=false
terraform validate
echo "PASS: terraform validate"

echo ""
echo "Optional (requires AWS credentials, still $0 if you do NOT type yes to apply):"
echo "  terraform plan"
echo ""
echo "=== Terraform static verification complete ==="
