# Threat model — initial draft

## Assets
Synthetic claim records; tenant and resource permissions; future tool responses and logs.

## Trust boundaries
1. Caller to application (identity not yet implemented)
2. Agent or other caller to read-only tools (untrusted input)
3. Tool gateway to backing data (authorization required before access)

## First threat: cross-tenant access
An employee of `northstar` supplies `tenant_id="harbor"` and reads `harbor` claim `C-1042` through a function that trusts the caller's tenant argument.

## Intended invariant
A verified principal associated with a tenant cannot retrieve a record from another tenant without an explicitly authorized exception.

## Slice 1A status
This first notebook *demonstrates* the vulnerability. No security controls or verified identity have been implemented; tests in this slice cannot establish security.
