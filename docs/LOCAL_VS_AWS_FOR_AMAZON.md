# Local Validation vs AWS Deploy — Which Is Better for Amazon SDE?

## Short answer

**For most Amazon SDE applicants: the local + Terraform (no apply) path is better.**

Use AWS deploy only if you will **operate it**, **measure ALB metrics**, and **discuss it deeply** in interviews.

## Comparison

| Factor | Local + IaC ($0) | Live AWS deploy ($$$) |
|--------|------------------|------------------------|
| **Cost** | Free | ~$50–150+/month if left running |
| **Proof of coding** | Strong (run `make verify`) | Same code path |
| **Proof of AWS knowledge** | Terraform + architecture docs | Hands-on ECS/RDS/ALB experience |
| **Performance claims** | Your hey artifacts (reproducible) | ALB-level metrics (different from local) |
| **Risk in interview** | Low if honest | High if you deployed once and forgot details |
| **Reviewer friction** | Clone → `make up` → verify in 2 min | Needs your AWS account or public URL |
| **CI authenticity** | GitHub Actions tests + terraform validate | + optional deploy workflow |

## What Amazon interviewers actually evaluate

1. **Can you build reliable backend services?** → Local stack proves this.
2. **Do you understand AWS building blocks?** → Terraform + `docs/AWS_ARCHITECTURE.md` prove design.
3. **Are metrics honest?** → Committed `results/hey_*.txt` + methodology.
4. **Operational thinking?** → Health checks, metrics, alarms in IaC, structured logs.

A shallow AWS deploy (apply once, destroy, empty AWS metrics section) is **weaker** than a deep local project with strong docs.

## When AWS deploy *is* better

Choose live AWS if **all** apply:

- You can afford teardown discipline (`terraform destroy`)
- You will run ALB load tests and fill AWS metrics honestly
- You can explain VPC, SGs, IAM roles, ECS deployments, and failures
- You want Solutions Architect–leaning stories (not just SDE coding)

## Recommended positioning on resume

**Best (honest, SDE-focused):**

```text
Built and load-tested a FastAPI ML inference API with Redis cache-aside and PostgreSQL logging (~713 req/s, ~108 ms p95, 0% errors). Designed AWS production topology (ECS Fargate, ALB, RDS, ElastiCache, S3, CloudWatch) in Terraform with CI validation.
```

**Only if actually deployed:**

```text
Deployed inference service on AWS ECS Fargate behind ALB with ElastiCache and RDS; sustained ___ req/s at ___ ms p95 (ALB metrics).
```

## Decision tree

```text
Need $0 and strong SDE story?
  → Local + make verify + metrics artifacts + Terraform validate

Have budget + time to operate AWS + interview prep on ops?
  → Apply Terraform + ALB load test + fill AWS metrics

Cannot afford AWS?
  → Do NOT claim "deployed to AWS"
```

## Verdict

| Profile | Winner |
|---------|--------|
| Amazon **SDE** (new grad / early career) | **Local + IaC + verification** |
| Amazon **Solutions Architect** | AWS deploy helps *if* you operate it |
| Strict **$0** | **Local only** |
| Maximum credibility per dollar | **Local + committed artifacts** |

Your current project is optimized for the **SDE winner** path.
