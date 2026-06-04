# Project Documentation Index

**Maintainer:** Roshini  
**Repository:** https://github.com/Rosh054/Scalable-Real-Time-Inference-Platform  
**Purpose:** Single entry point for all official project documentation. Use this index when responding to academic, internship, or employment enquiries.

---

## Official records (use for letters and verification)

| Document | Audience | Description |
|----------|----------|-------------|
| **[FORMAL_PROJECT_DOCUMENTATION.md](FORMAL_PROJECT_DOCUMENTATION.md)** | Institution, referees, HR, audit | **Primary formal record** — abstracts, architecture, scope, metrics, deployment status, maintenance |
| **[Roshini_Scalable_Real-Time_Inference_Platform_Formal.pdf](Roshini_Scalable_Real-Time_Inference_Platform_Formal.pdf)** | Institution, print/submit | **Primary PDF** — abstracts, maintenance record, full project detail |
| **[Scalable_Real-Time_Inference_Platform_Formal_Document.pdf](Scalable_Real-Time_Inference_Platform_Formal_Document.pdf)** | Institution | Previous PDF export (regenerate: `make pdf`) |
| **[../results/metrics_template.md](../results/metrics_template.md)** | Technical reviewers | Recorded load-test metrics with artifacts |
| **[VERIFICATION.md](VERIFICATION.md)** | Third-party verifiers | Step-by-step reproduction of claims |

---

## Abstracts (copy for submissions)

### Academic project

**Title:** Scalable Real-Time Inference Platform on AWS  

**Abstract (short):**  
This project builds a scalable cloud-based machine learning inference platform using AWS ECS, Docker, Redis, PostgreSQL, and CloudWatch. It supports low-latency REST API predictions, caching, request logging, auto-scaling (IaC), CI/CD deployment, and monitoring, demonstrating a production-style system for reliable real-time AI model serving. Application behaviour is validated locally with documented load-test results; AWS infrastructure is defined in Terraform.

*Full formal version: Section 3 of [FORMAL_PROJECT_DOCUMENTATION.md](FORMAL_PROJECT_DOCUMENTATION.md)*

---

### Internship

**Title:** Cloud-Native Backend and Distributed Systems Internship  

**Abstract (short):**  
This internship work develops scalable backend services using FastAPI, Redis, PostgreSQL, Docker, AWS-oriented architecture, and CI/CD workflows. Deliverables include REST APIs, distributed caching, database audit logging, health and metrics endpoints, containerised deployment, and Terraform-based cloud infrastructure design for operational monitoring and scaling.

*Full formal version: Section 4 of [FORMAL_PROJECT_DOCUMENTATION.md](FORMAL_PROJECT_DOCUMENTATION.md)*

**Clarification for enquiries:** Current codebase implements **synchronous inference** and does not include separate async worker queues; see Section 12 of the formal documentation.

---

## Technical documentation

| Document | Topic |
|----------|--------|
| [../README.md](../README.md) | Quick start, commands, overview |
| [AWS_ARCHITECTURE.md](AWS_ARCHITECTURE.md) | AWS topology, Well-Architected mapping |
| [LOCAL_TO_AWS_MAPPING.md](LOCAL_TO_AWS_MAPPING.md) | Docker Compose ↔ AWS services |
| [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md) | ADRs |
| [../terraform/README.md](../terraform/README.md) | Optional AWS deploy and teardown |
| [AMAZON_SDE_PORTFOLIO.md](AMAZON_SDE_PORTFOLIO.md) | Interview preparation (optional) |
| [LOCAL_VS_AWS_FOR_AMAZON.md](LOCAL_VS_AWS_FOR_AMAZON.md) | Local vs live AWS comparison |

---

## Evidence artifacts (repository)

| Artifact | Location |
|----------|----------|
| Load test output | `results/hey_*.txt` |
| Metrics summary | `results/metrics_template.md` |
| CI workflows | `.github/workflows/ci.yml`, `terraform.yml` |
| IaC | `terraform/*.tf` |

---

## Standard responses for common enquiries

**Q: Was this deployed on AWS?**  
A: The production stack is **fully defined in Terraform**. The application is **validated locally** with Docker Compose and load tests. Live AWS deployment is **optional** and documented in `terraform/README.md`.

**Q: What performance was achieved?**  
A: See `results/metrics_template.md` (e.g. ~713 req/s, ~108 ms p95, 0% errors, ~99.9% cache hit rate under repeated-payload test).

**Q: How can we verify the project?**  
A: Follow `docs/VERIFICATION.md` or run `make up && make verify`.

**Q: Who maintains this repository?**  
A: Roshini (document owner). Updates to formal documentation are required when scope or deployment status changes.

---

*Last updated: June 2026*
