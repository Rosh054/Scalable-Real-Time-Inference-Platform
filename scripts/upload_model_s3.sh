#!/usr/bin/env bash
# Upload trained model to S3 bucket from Terraform output
set -euo pipefail

BUCKET="${1:-}"
KEY="${2:-models/model.joblib}"
MODEL_PATH="${3:-models/model.joblib}"

if [[ -z "$BUCKET" ]]; then
  echo "Usage: $0 <s3-bucket> [s3-key] [local-path]"
  echo "  Or:  $0 \$(terraform -chdir=terraform output -raw s3_model_bucket)"
  exit 1
fi

if [[ ! -f "$MODEL_PATH" ]]; then
  echo "Model not found at $MODEL_PATH. Run: make train-model"
  exit 1
fi

aws s3 cp "$MODEL_PATH" "s3://${BUCKET}/${KEY}"
echo "Uploaded to s3://${BUCKET}/${KEY}"
