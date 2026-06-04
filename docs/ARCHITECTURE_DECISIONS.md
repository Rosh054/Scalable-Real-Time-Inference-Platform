# Architecture Decision Records (ADR)

## ADR-001: Validate locally; treat AWS as designed target

**Status:** Accepted

**Context:** Amazon interviews need proof of engineering without requiring paid AWS for every candidate.

**Decision:** Run full application stack on Docker Compose; ship Terraform for ECS/ALB/RDS/ElastiCache/S3/CloudWatch; validate IaC with `terraform validate` in CI.

**Consequences:** Reviewers can reproduce behavior in minutes. Resume claims must distinguish "load-tested locally" vs "deployed on AWS."

---

## ADR-002: Cache-aside with deterministic input hashing

**Status:** Accepted

**Context:** Repeated inference requests dominate ML serving traffic.

**Decision:** SHA-256 hash of normalized JSON (`sort_keys=True`) as Redis key; TTL from `CACHE_TTL_SECONDS`.

**Consequences:** ~99.9% cache hit rate under repeated-payload load tests; cache hit flag stored in DB and `/metrics`.

---

## ADR-003: Log every prediction to PostgreSQL

**Status:** Accepted

**Context:** Auditability and debugging for production inference.

**Decision:** Insert row per `/predict` with `request_id`, `input_hash`, payload, latency, `cache_hit`.

**Consequences:** Slight write latency; strong interview narrative on observability and compliance-style logging.

---

## ADR-004: JSON logs in AWS environment

**Status:** Accepted

**Context:** CloudWatch Logs Insights queries expect structured JSON.

**Decision:** When `APP_ENV=aws`, emit JSON log lines with `request_id`, `cache_hit`, `latency_ms`.

**Consequences:** Local dev keeps human-readable logs; AWS path matches production conventions.

---

## ADR-005: X-Request-ID middleware

**Status:** Accepted

**Context:** Distributed tracing and ALB → ECS correlation in interviews.

**Decision:** Middleware sets/propagates `X-Request-ID`; `/predict` uses same ID in response and DB.

**Consequences:** Aligns with Amazon operational excellence talking points.
