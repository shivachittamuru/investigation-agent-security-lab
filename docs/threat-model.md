# Threat Model — Investigation Agent Security Lab

## Purpose and scope

This document describes the *implemented educational lab*, not a production security assessment. The scenario uses synthetic insurance-claim data for `northstar` and `harbor`, including intentionally overlapping claim IDs. The assistant may propose tool calls and recommendations; only trusted application boundaries should authorize access and consequential actions.

## Assets and security objectives

| Asset | Primary objective |
| --- | --- |
| Tenant-scoped claim records | No unauthorized cross-tenant or cross-claim disclosure |
| Signed lab credentials and principal context | Do not trust caller/model-asserted employee or tenant identity |
| Access grants / employee eligibility | Deny requests without valid, current authorization (freshness is an open gap) |
| Retrieved documents and model-generated tool calls | Do not promote untrusted text into privileged instructions |
| Evaluation records and tool outcomes | Record attempted actions separately from control decisions and results |
| Coverage evidence and payout recommendations | Verify factual basis before policy evaluation; no unapproved payment execution |

## Trust boundaries

1. **HTTP caller → API:** Bearer tokens are validated, and identity is resolved from the trusted employee directory. Body fields must not dictate identity or tenant scope.
2. **Model → tool gateway:** Tool names and arguments are untrusted. Server-controlled `InvestigationContext` supplies principal, data, and grants. Tool-level authorization determines whether a claim can be retrieved.
3. **Untrusted documents → model:** Customer documents and retrieval results are evidence, not system instructions. Indirect prompt injection can still induce undesirable model actions.
4. **Tool results → evaluation:** The evaluator should identify attempted unauthorized actions, actual denials, resource disclosures, and legitimate work progress independently.
5. **Candidate facts → business policy:** Structured model extraction and source IDs are unverified until checked against authoritative sources. **This verification boundary is proposed, not yet implemented.**
6. **Recommendation → consequential action:** Model recommendations must not grant approval or payment-execution authority. The repository currently demonstrates policy helpers only; it has no payment API or human approval workflow.

## Implemented controls and observations

- **Resource scoping:** Tenant- and claim-specific grants checked before returning a claim. An intentionally insecure lookup remains available solely as a teaching counterexample.
- **Identity:** A lab JWT verifier checks signature, issuer, audience, and expiry; employee membership/active status is checked separately.
- **API boundary:** A FastAPI endpoint derives a trusted principal and runs a registered LangGraph claim tool; extra identity fields in the request body are rejected.
- **Prompt-injection observation:** A model requested Northstar claim `C-1043` after seeing a retrieved document referencing it; Alice's gateway permission allowed only `C-1042`, and the request was denied. This observation alone does not prove injection causation.
- **Trajectory evaluation:** Deterministic replay separates attempted calls, authorization denials, boundary violations, and evidence retrieval. The recovery demonstration uses a *scripted* sequence rather than a live autonomous agent continuation.
- **Decision policy:** Synthetic coverage/evidence inputs and a $5,000 illustrative review threshold lead to review/needs-evidence outcomes. The AI cannot approve or execute payment through the policy helper; the helper has not been installed at a real execution gateway.

## Key threats and remaining gaps

| Threat / failure mode | Current mitigation | Remaining limitation |
| --- | --- | --- |
| Cross-tenant/cross-claim data access | Trusted tenant context and per-claim grants | Grant freshness and all-tool consistency need hardening |
| Forged or expired credential | Token verification and employee lookup | Educational HS256 signing; no production IdP integration or full session lifecycle |
| Indirect prompt injection | Deterministic tool permission boundary | Model behavior can still be redirected; attack causation/coverage are limited |
| Stale eligibility during long-running execution | Eligibility refreshed at HTTP entry | No per-sensitive-action revocation check |
| Unsupported payout recommendation | Deterministic policy with evidence prerequisites | Inputs to `VerifiedEvidence` are not yet independently authenticated |
| Forged approval/source reference | **Planned Slice 4B** provenance registry | No authoritative evidence verifier implemented yet |
| Unauthorized consequential execution | No payment/approval operations exposed; action helper denies agent actions | Real enforcement and human approval flow unimplemented |
| Missing incident/audit evidence | Tests and basic evaluation records | No tamper-resistant audit store or production telemetry pipeline |
| Runaway tool/model cost or unbounded retries | Controlled notebook experiments | No general runtime limits, budgets, or admission control yet |

## Non-goals and assumptions

- No real customer or financial data, no real payment operations, and no claims adjudication.
- The synthetic records and local files are treated as trusted only for the specific experiment; a production solution needs access-controlled authoritative services, freshness guarantees, evidence integrity, and operational auditing.
- A passing test proves only its stated invariant under the tested inputs. It is not evidence of universal prompt-injection resilience, regulatory compliance, or production readiness.

## Next planned investigation

**Slice 4B — Evidence Provenance & Trust Boundaries:** Resolve model-extracted source references against a trusted, claim- and tenant-scoped registry; reject missing, forged, inactive, ambiguous, or cross-tenant references; populate trusted policy inputs only from authoritative records. Implement and verify before marking this boundary complete.
