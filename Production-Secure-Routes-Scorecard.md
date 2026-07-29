<!-- YXZYS | saeng-il ai [research] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# Production Secure Routes Scorecard

## Executive Summary

ARCHMAGE is a Python library for deterministic, pre-execution policy decisions
around coding-agent tool actions. It has no HTTP server, database, browser client,
GraphQL resolver, WebSocket, or desktop IPC implementation. The production trust
boundary is therefore a host-runtime call into one of two adapters, followed by
the policy enforcement point (PEP) and decision point (PDP).

The package uses a `src` layout, has no runtime dependencies, and is prepared for
CI across Python 3.9–3.13. Release automation builds distributions, checks
metadata and package contents, creates checksums and an SPDX SBOM, and requests
GitHub artifact attestations. Documentation has a separate GitHub Pages workflow.

Authentication is not implemented by the library. The host supplies `actor_id`,
`task_id`, workspace, and revision metadata; ARCHMAGE validates their shape but
does not cryptographically authenticate them. Authorization is deterministic
policy evaluation. The highest risks are host bypass of the adapters, self-asserted
identity, coarse tool-argument validation, and the lack of host-level invocation
rate limiting.

## Discovery Inventory

- **Codebase:** Python library under `src/archmage`, with adapters, runtime,
  evaluators, doctrine data, tests, documentation, and deterministic eval runners.
- **CI/CD:** `.github/workflows/ci.yml`, `release.yml`, and `docs.yml`; Dependabot
  updates Python and GitHub Actions dependencies.
- **Authentication and identity:** required metadata is validated by
  `AdapterExecutionContext`, but authentication and credential verification are
  explicitly delegated to the embedding host.
- **Authorization:** `PolicyEnforcementPoint` routes proposals to a fail-closed
  `PolicyDecisionPoint`; verdicts can allow, obligate, repair, deny, or escalate.
- **Input validation:** adapters require non-empty tool identity, mandatory
  execution context, an absolute workspace, an immutable hexadecimal revision,
  canonical JSON arguments, a 1 MiB payload ceiling, a small tool registry, and
  a required path field per registered tool.
- **Client wiring:** no web, mobile, Electron, Tauri, or native bridge was found.
  The generic and Antigravity adapters are library-call integration boundaries.
- **Route topology:** no network routes or RPC endpoints were found. The matrix
  scores the three callable enforcement channels that accept host-controlled data.

## Indexed Route Validation Matrix

| Index | Route/Endpoint | Consumer (Desktop/Web) | Auth Status | Validation | Total Score | Remediation |
|---:|---|---|---|---|---:|---|
| 1 | Library: `GenericAdapter.intercept_tool_call` | Host runtime (desktop/CLI) | Declared identity only; host must authenticate | Required context, immutable revision, absolute workspace, canonical JSON arguments, 1 MiB limit, explicit two-tool registry, and required path field; argument schema remains incomplete | 68 | Require a verified host principal, strict per-tool schemas, and host rate limits before privileged dispatch. |
| 2 | Library: `AntigravityAdapter.intercept_tool_call` | Antigravity host runtime | Declared identity only; host must authenticate | Same boundary validation as the generic adapter; an explicit four-tool registry rejects unknown tools and missing paths | 70 | Bind authenticated principal and capabilities to context; add strict schemas and host rate limits. |
| 3 | Library: `PolicyEnforcementPoint.intercept` | Embedding application | No authentication; receives an in-process proposal | Typed proposal, fail-closed evaluator aggregation, obligation/repair enforcement, and audit-context derivation; no independent payload ceiling | 70 | Expose only behind a validated adapter or add a validated proposal factory and invocation budget. |

Scores use the required 100-point rubric. Identity declaration earned partial
authentication credit, policy evaluation earned authorization credit, validation
earned credit where code evidence exists, the payload ceiling earned partial
abuse-control credit, and safe typed failures earned data-exposure credit. No
channel received full authentication or rate-limiting credit because those
controls are absent by design.

## Top Risks

1. **Self-asserted identity:** an untrusted caller can supply any `actor_id`.
   Shape validation is not proof of identity, so a privileged host must bind the
   metadata to its own authenticated principal.
2. **Adapter bypass:** direct tool execution outside the adapter is invisible to
   ARCHMAGE. Hosts must make the adapter the sole privileged dispatch path and
   constrain direct shell, filesystem, and network access separately.
3. **Coarse input schemas and rate control:** the common boundary limits total
   payload size and shipped adapters reject unknown tools, but they do not define
   strict full-argument schemas or invocation budgets. Novel argument keys and
   high request frequency remain host risks.

## Action Items

### 1. Bind host authentication to adapter context

Target: host integration before `GenericAdapter.intercept_tool_call`.

```python
principal = host_auth.require_principal(request)
context_meta = {
    "task_id": request.task_id,
    "actor_id": principal.stable_id,
    "workspace": workspace_registry.require_owned(principal, request.workspace),
    "git_sha": repository.require_current_revision(),
    "environment": deployment.environment,
}
adapter.intercept_tool_call(request.tool, request.arguments, context_meta)
```

Do not copy identity or workspace authority directly from an untrusted request.

### 2. Add strict per-tool schemas and an invocation budget

Target: host integration before either adapter.

```python
schema = TOOL_SCHEMAS.get(request.tool)
if schema is None:
    raise PermissionError("Tool is not registered")
arguments = schema.parse_strict(request.arguments)
rate_limiter.consume(key=principal.stable_id, cost=tool_cost(request.tool))
adapter.intercept_tool_call(request.tool, arguments, context_meta)
```

The schema should reject unknown keys, constrain strings and collections, and
normalize paths before the proposal reaches a privileged executor.

### 3. Make the validated dispatch path non-bypassable

Target: host tool registry.

```python
def dispatch(request, principal):
    if not adapter.intercept_tool_call(request.tool, request.arguments, context(principal)):
        raise PermissionError("Policy did not authorize dispatch")
    return PRIVATE_EXECUTORS[request.tool](**request.arguments)
```

Keep `PRIVATE_EXECUTORS` unavailable to agent/plugin code and run high-risk tools
inside an operating-system sandbox with separate filesystem and network controls.

## Evidence Notes

- Inspected `pyproject.toml`, `.github/workflows`, `.github/dependabot.yml`,
  `src/archmage/adapters`, `src/archmage/runtime`, `tests`, `docs`, and `evals`.
- Targeted route/auth searches found no web framework, controller, client API,
  GraphQL, WebSocket, IPC, session, JWT, OAuth, or database implementation.
- `src/archmage/adapters/_context.py` contains the shared metadata and payload
  boundary. `generic.py` and `antigravity.py` map host calls into proposals.
- `src/archmage/runtime/pdp.py` contains both the PEP and the fail-closed PDP.
- The scores assess only repository evidence. Host authentication, rate limiting,
  sandboxing, executor privacy, and deployment settings cannot be verified here.
