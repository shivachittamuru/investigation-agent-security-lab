# Investigation Agent Security Lab

A hands-on Python reference implementation for securing and evaluating AI agents through identity, authorization, prompt-injection testing, audit, and reliability controls.

## Learning approach

Understand → Experiment → Break → Fix → Verify → Review.

This repository is an educational security lab, **not a production-ready security system**. All records are synthetic. Intentionally insecure examples are labeled and must never be deployed or connected to real data.

## Current scope

**Slice 1A:** a small deterministic CSV dataset and an intentionally insecure read function to illustrate missing resource authorization. No real identity verification or secure authorization has been implemented yet.

### Setup (PowerShell, from the repository root)

```powershell
uv sync
uv run jupyter lab
```

Open `notebooks/01_authorization_first_failure.ipynb` and run the cells in order. Do not use real customer data or credentials.

### Tests

```powershell
uv run pytest -q
```

The initial tests verify the synthetic fixture and demonstrate that the **insecure example** permits a cross-tenant read. They are *not* evidence that the application is secure.

## Roadmap

1. Small synthetic dataset and first unsafe lookup
2. Verified principal and authorization-aware gateway
3. Deterministic security tests
4. Read-only investigation and agent tool integration
5. Adversarial documents and evaluations
6. Reliability, budgets, and audit
7. Code review and selective managed-service integration
