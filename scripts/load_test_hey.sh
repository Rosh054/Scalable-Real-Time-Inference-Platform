#!/usr/bin/env bash
# Load test with hey (https://github.com/rakyll/hey)
# Install: go install github.com/rakyll/hey@latest  OR  brew install hey
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
DURATION="${DURATION:-30s}"
CONCURRENCY="${CONCURRENCY:-50}"
OUTPUT_DIR="${OUTPUT_DIR:-results}"

mkdir -p "$OUTPUT_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUT_FILE="$OUTPUT_DIR/hey_${TIMESTAMP}.txt"

PAYLOAD='{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'

echo "=== hey load test ===" | tee "$OUT_FILE"
echo "Target: $BASE_URL/predict" | tee -a "$OUT_FILE"
echo "Duration: $DURATION, Concurrency: $CONCURRENCY" | tee -a "$OUT_FILE"
echo "" | tee -a "$OUT_FILE"

if ! command -v hey &> /dev/null; then
  echo "ERROR: 'hey' not found. Install: brew install hey" | tee -a "$OUT_FILE"
  exit 1
fi

hey -z "$DURATION" -c "$CONCURRENCY" -m POST \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  "$BASE_URL/predict" 2>&1 | tee -a "$OUT_FILE"

echo "" | tee -a "$OUT_FILE"
echo "=== Application metrics (after load) ===" | tee -a "$OUT_FILE"
curl -s "$BASE_URL/metrics" | tee -a "$OUT_FILE"
echo "" | tee -a "$OUT_FILE"
echo "Results saved to $OUT_FILE"
echo "Copy latency percentiles and cache_hit_rate into results/metrics_template.md"
