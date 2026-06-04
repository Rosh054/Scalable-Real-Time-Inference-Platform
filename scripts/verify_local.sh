#!/usr/bin/env bash
# Reproducible verification for recruiters/reviewers ($0 AWS cost).
# Usage: ./scripts/verify_local.sh
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Inference Platform — Local Verification ==="
echo "Base URL: $BASE_URL"
echo ""

fail() { echo "FAIL: $1"; exit 1; }
pass() { echo "PASS: $1"; }

# Health
HEALTH=$(curl -sf "$BASE_URL/health" || fail "API not reachable at $BASE_URL (run: make up)")
echo "$HEALTH" | grep -q '"status":"healthy"' && pass "/health healthy" || fail "/health not healthy"

# Predict (uncached-style fresh key)
PRED=$(curl -sf -X POST "$BASE_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{"sepal_length":6.0,"sepal_width":2.9,"petal_length":4.5,"petal_width":1.5}')
echo "$PRED" | grep -q '"prediction"' && pass "/predict returns prediction"
echo "$PRED" | grep -q '"request_id"' && pass "/predict returns request_id"
curl -sf -D - -o /dev/null -X POST "$BASE_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}' 2>/dev/null | grep -qi 'X-Request-ID' && pass "X-Request-ID response header"

# Cache hit
PRED2=$(curl -sf -X POST "$BASE_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{"sepal_length":6.0,"sepal_width":2.9,"petal_length":4.5,"petal_width":1.5}')
echo "$PRED2" | grep -q '"cache_hit":true' && pass "Redis cache-aside (repeat request)"

# Metrics
METRICS=$(curl -sf "$BASE_URL/metrics")
echo "$METRICS" | grep -q 'inference_predictions_total' && pass "/metrics Prometheus-style"

# Model info
curl -sf "$BASE_URL/model-info" | grep -q '"model_name"' && pass "/model-info"

# Artifact files
test -f models/model.joblib && pass "Model artifact exists"
test -f results/metrics_template.md && pass "Documented load-test metrics template"

if [[ -f results/hey_20260601_143951.txt ]]; then
  pass "Load test artifact (hey) present"
fi

echo ""
echo "=== All local verification checks passed ==="
echo "See docs/VERIFICATION.md for full reviewer guide."
