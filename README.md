# Investigation Agent Security Lab

A hands-on, local-first Python reference implementation for learning how to secure and evaluate AI agents through identity, authorization, prompt-injection testing, evidence verification, and controlled decision-making.

**Learning loop:** Understand → Experiment → Break → Fix → Verify → Review.

> **Educational project, not production-ready.** All insurance data is synthetic. Intentionally insecure examples are for teaching only. Do not deploy them or connect the lab to real customer data. The lab's JWT scheme, CSV-backed directory, and grant checks are not production-ready identity or authorization services.

## Scenario and security goals

An insurance investigation assistant helps employees examine claims. Two synthetic tenants, `northstar` and `harbor`, deliberately reuse claim IDs such as `C-1042`. An agent can propose actions, but trusted application code must independently establish **who** is acting, **which resources** they can access, **what controls** were applied, and **which business decisions** may follow.

The security questions are distinct:

1. **Identity:** Has the caller been authenticated, and is the employee eligible?
2. **Authorization:** Can this employee read this tenant's specific claim?
3. **Agent behavior:** Did lower-trust documents influence model-generated tool calls?
4. **Evaluation:** What did the agent attempt, what was blocked, and did authorized work continue?
5. **Decision governance:** Do verified facts support the recommendation, and who may approve or execute an action?

## Learning path and implementation status

| Notebook | Topic | Implemented lesson |
| --- | --- | --- |
| [01 — Authorization first failure](notebooks/01_authorization_first_failure.ipynb) | Insecure claim lookup | Demonstrates an intentional cross-tenant data access vulnerability. |
| [02 — Resource authorization](notebooks/02_resource_authorization.ipynb) | Scoped access grants | Introduces a trusted principal, tenant-scoped grant checks, and an authorization-aware LangGraph tool. |
| [03 — Verified identity](notebooks/03_verified_identity.ipynb) | Lab JWT verification | Verifies token signature/issuer/audience/expiry and resolves employee eligibility using trusted directory data. |
| [04 — API authentication](notebooks/04_api_authentication.ipynb) | FastAPI boundary | Authenticates bearer tokens, rejects spoofed body identity, and injects trusted context into LangGraph tooling. |
| [05 — Indirect prompt injection](notebooks/05_indirect_prompt_injection.ipynb) | Untrusted retrieved documents | Records a model proposing an unauthorized claim lookup and the tool gateway denying it. |
| [06 — Adversarial evaluation](notebooks/06_adversarial_evaluation.ipynb) | Tool trajectories and scripted recovery | Distinguishes unauthorized attempts, control decisions, boundary violations, legitimate evidence retrieval, and scripted continuation. |
| [07 — Evidence and decision policy](notebooks/07_evidence_and_decision_policy.ipynb) | Evidence sufficiency and payout rules | Demonstrates a deterministic review threshold, missing-evidence outcomes, and read-only agent action limits. |

The implementation lives under `src/investigation_agent_security_lab/` with regression tests in `tests/security/`. A recorded adversarial case is stored under `evals/adversarial/`.

### What the current evidence supports—and does not support

- **Supported:** In the recorded experiment, the model requested `get_claim(C-1043)` and the authorization tool denied it. The lab also contains automated tests for authorization, API identity, tool boundaries, scripted recovery, and decision policy.
- **Not established:** That prompt injection *caused* the cross-claim request in every run, or that the model can autonomously recover from a denial. Notebook 06's recovery demonstration uses scripted calls, not actual post-denial model continuation.
- **Not established:** That an insurance claim is covered or payable. `VerifiedEvidence` in the current policy module is an input contract; the repository does **not yet** contain an authoritative provenance verifier. A correct amount/status comparison is not a sufficient coverage determination.
- **Not implemented:** A payment service, actual supervisor-approval workflow, durable audit store, operating budgets, or fully managed security services.

## Quick start (PowerShell and VS Code)

From the repository root:

```powershell
uv sync
uv run pytest -q
```

Open the repository in VS Code, choose the project's `uv` environment as the Jupyter kernel, and run notebooks under `notebooks/` in order. You do **not** need a separate JupyterLab server, though you may use one if preferred:

```powershell
uv run jupyter lab
```

Notebook 05 contains an optional Microsoft Foundry model experiment. To run those cells, copy `.env.example` to the gitignored `.env`, configure your existing Foundry project endpoint/model deployment, and authenticate using your development Azure identity. The deterministic regression tests should not require a live model or cloud deployment. Never commit secrets or tokens.

## Repository layout

```text
notebooks/                          Cell-by-cell lessons and experiments
data/synthetic/                     Synthetic claims, employees, grants, documents
src/investigation_agent_security_lab/
                                    Identity, claims, tools, API, policy, evaluation
tests/security/                     Deterministic regression tests
evals/adversarial/                  Recorded model-attack observations
docs/threat-model.md                Assets, trust boundaries, controls, limitations
```

## Core principles

- **Authentication ≠ authorization.** A valid token does not authorize every claim.
- **Tool arguments are untrusted.** The agent selects a claim ID, but the application supplies trusted identity and enforces resource scope.
- **Documents are data, not policy.** A retrieved document must not create permissions or override system instructions.
- **Observe the whole trajectory.** A blocked unauthorized action, successful recovery, and final business outcome are separate measurements.
- **References are not proof.** An extracted `source_id` does not establish that coverage or approval was independently verified.
- **Recommendation ≠ execution.** The agent may recommend; it must not approve claims or send payouts merely because a policy threshold appears satisfied.

## Next increments and known gaps

| Workstream | Status / limitation |
| --- | --- |
| **Slice 4B: evidence provenance and trust promotion** | **Proposed:** a trusted tenant/claim-scoped registry to resolve source references and supply verified evidence to decision policy. No `evidence_verifier.py` in the repository yet. |
| Real model continuation | **Future:** exercise an actual multi-step model/tool cycle after access denial. Current recovery examples are scripted. |
| Authorization freshness | **Gap:** employee eligibility is reloaded per HTTP request, while grants are snapshotted at app startup; no mid-execution revocation enforcement. |
| Decision-action enforcement | **Gap:** policy/action helpers are not wired into a real approval/payment execution boundary. |
| Governance & reliability | **Planned:** audit, evidence trails, cost/token budgets, resilience tests, and selective managed-service integration. |

See [Threat Model](docs/threat-model.md) for the security assumptions and attack surfaces.

## Testing and safe experimentation

```powershell
uv run pytest -q
```

Use synthetic data, isolate deliberately insecure demonstrations, and add deterministic regression assertions for each proven boundary. Passing tests demonstrate the tested invariants—not security certification or complete coverage of possible model behavior.
