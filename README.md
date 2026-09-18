<!-- YXZYS | saeng-il ai [development] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->
<!-- mcp-name: io.github.YXZYSME/archmage -->

<div align="center">
  <img src="assets/banner.jpg" alt="ARCHMAGE" width="400">

  # ARCHMAGE

  **saeng-il ai [ research | development | integration ]**

  Deterministic pre-execution control for coding-agent actions.

  [![CI](https://github.com/YXZYSME/archmage/actions/workflows/ci.yml/badge.svg)](https://github.com/YXZYSME/archmage/actions/workflows/ci.yml)
  [![Python](https://img.shields.io/badge/Python-3.9–3.13-3776AB.svg)](https://www.python.org/)
  [![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
</div>

> Current release: `v2.0.0`. Python distributions are published as
> [`archmage-ai`](https://pypi.org/project/archmage-ai/); the portable Agent
> Plugin is attached separately to the GitHub release.

ARCHMAGE evaluates a proposed tool action before an adapter dispatches it. The
runtime converts the proposal into a stable digest, runs deterministic policy
evaluators, and emits one typed decision:

`ALLOW` · `ALLOW_WITH_OBLIGATIONS` · `REPAIR` · `DENY` · `ESCALATE`

It is designed for coding-agent file writes, command proposals, protected-policy
changes, declared scope, artifact lineage, identity, and evidence obligations.

## Two-minute example

```python
from dataclasses import replace

from archmage import (
    ActionProposal,
    ActorIdentity,
    PolicyContext,
    create_default_policy_decision_point,
)

pdp = create_default_policy_decision_point()
context = PolicyContext(
    workspace="/workspace/project",
    environment="local",
    audit_logger_configured=True,
)
proposal = ActionProposal(
    task_id="task-42",
    actor=ActorIdentity(actor_id="coding-agent", actor_type="agent"),
    operation="write_file",
    tool="write_to_file",
    arguments={"TargetFile": "../outside.py"},
    target_paths=["../outside.py"],
    requested_side_effects=[],
    repository_revision="0123456789abcdef0123456789abcdef01234567",
    environment="local",
)

blocked = pdp.evaluate(proposal, context)
print(blocked.decision)  # VerdictDecision.DENY

narrowed = replace(
    proposal,
    arguments={"TargetFile": "src/feature.py"},
    target_paths=["src/feature.py"],
)
allowed = pdp.evaluate(narrowed, context)
print(allowed.decision)  # VerdictDecision.ALLOW
```

The adapter or executor must refuse dispatch unless the returned decision permits
it. ARCHMAGE does not independently intercept arbitrary operating-system activity.

## Install and verify

Install the signed package release:

```bash
python -m pip install archmage-ai
```

For development from a reviewed checkout:

```bash
python -m pip install --editable ".[dev]"
python -m pytest
```

Release wheels and source distributions are built in GitHub Actions, accompanied
by SHA-256 checksums, an SPDX SBOM, and GitHub artifact attestations. Verification
instructions are in the [supply-chain guide](docs/supply-chain.md).

## Agent Plugin

ARCHMAGE also ships a separate, self-contained Agent Plugins 1.0.0 ZIP. The
plugin is an interoperability and distribution adapter: its Agent Skill tells a
compatible host when to invoke the bundled MCP tools, while those tools route
every decision through the same Python `PolicyEnforcementPoint` used by native
integrations.

The ZIP is deliberately separate from the wheel and source distribution. It is
validated against vendored Agent Plugins schemas, smoke-tested directly from an
extracted archive, and never submitted to PyPI or Python metadata validation.
See the [Agent Plugin guide](docs/agent-plugin.md) for the trust boundary and
installation sequence.

## MCP clients (local stdio)

ARCHMAGE's MCP server is local stdio only. There is no hosted URL. Official
registry name: `io.github.YXZYSME/archmage`.

Install the package, then point the client at `python -m archmage.mcp` or the
`archmage-mcp` console script. Both require an audit-log path via
`ARCHMAGE_AUDIT_LOG` or `--audit-log`.

```bash
python -m pip install archmage-ai
mkdir -p "$HOME/.archmage"
```

### Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "archmage": {
      "command": "python",
      "args": ["-m", "archmage.mcp"],
      "env": {
        "ARCHMAGE_AUDIT_LOG": "/ABS/PATH/TO/archmage-audit.jsonl"
      }
    }
  }
}
```

Equivalent after `archmage-mcp` is on `PATH`:

```json
{
  "mcpServers": {
    "archmage": {
      "command": "archmage-mcp",
      "env": {
        "ARCHMAGE_AUDIT_LOG": "/ABS/PATH/TO/archmage-audit.jsonl"
      }
    }
  }
}
```

### Claude Code / Claude CLI

```bash
claude mcp add --transport stdio archmage \
  --env ARCHMAGE_AUDIT_LOG="$HOME/.archmage/audit.jsonl" \
  -- python -m archmage.mcp
```

```bash
claude mcp add --transport stdio archmage \
  --env ARCHMAGE_AUDIT_LOG="$HOME/.archmage/audit.jsonl" \
  -- archmage-mcp
```

Claude Code can also install the PreToolUse plugin from this repository:

```text
/plugin marketplace add YXZYSME/archmage
/plugin install archmage@archmage
```

### Cursor (`.cursor/mcp.json` or `mcp.json`)

```json
{
  "mcpServers": {
    "archmage": {
      "command": "python",
      "args": ["-m", "archmage.mcp"],
      "env": {
        "ARCHMAGE_AUDIT_LOG": "/ABS/PATH/TO/archmage-audit.jsonl"
      }
    }
  }
}
```

Replace `/ABS/PATH/TO/archmage-audit.jsonl` with a real writable path. Registry
listing steps that a maintainer must still perform by hand are in
[REGISTRY_SUBMISSIONS.md](REGISTRY_SUBMISSIONS.md). MCPB / Smithery path B is
documented in [docs/mcpb.md](docs/mcpb.md).

## What is included

- Eleven deterministic core evaluators with fail-closed aggregation.
- A generic tool-call adapter with explicit identity, workspace, and immutable
  revision requirements and canonical JSON payload validation.
- A reference Antigravity adapter.
- Digest-bound, verifier-backed, single-use approval records for destructive and
  shell-command obligations.
- Contract evaluators for interface depth and contract-first Python changes.
- Reproducible gold-case, repair-loop, policy-drift, and latency benchmarks.
- An Apache-2.0 licensed skill and doctrine bundle.
- A portable Agent Plugins 1.0.0 edge adapter with durable JSONL audit records.

## Validated release-candidate benchmarks

The latest hosted candidate evidence is produced by the
[revision-bound CI workflow](https://github.com/YXZYSME/archmage/actions/workflows/ci.yml).
Every JSON artifact records the exact commit, case catalog, Python version, and
runner platform. Signed release artifacts will supersede this release-candidate snapshot.

| Suite | Result | Scope |
|---|---:|---|
| Gold-case compliance | 13/13 exact; 0 false positives; 0 false negatives | Fixed catalog, 11 default evaluators |
| Repair loop | 2/2 compliant after one retry | Fixed machine-readable repairs |
| Indirect-instruction subset | 2/2 dangerous proposals denied | Tool proposals attributed to untrusted repository text |
| Full-PDP overhead | 0.348455 ms p95; 3,132.472 evaluations/s | 5,000 iterations on hosted Linux, CPython 3.13.14 |

These are deterministic proposal-level results from one recorded environment,
not claims of universal agent safety or platform-wide performance. See the
[benchmark guide](docs/benchmarks.md) and [security claims policy](docs/security-claims.md).

## Security boundary

ARCHMAGE is a policy decision and enforcement library, not a sandbox, firewall,
credential vault, malware scanner, or complete prompt-injection defense. Its
guarantees depend on every relevant tool call passing through a correctly wired
adapter, on the host preventing bypass around that adapter, and on the host
authenticating any approval record before its verifier accepts it.

Read [limitations](docs/limitations.md) before integrating it with privileged
tools. Report suspected vulnerabilities through the private route documented in
`SECURITY.md` once that release-gate policy is approved.

## Documentation

- [Published documentation](https://archmage.saengil.ai/)
- [Documentation source](docs/index.md)
- [Changelog](CHANGELOG.md)
- [Site implementation handoff](docs/specs/archmage-site/README.md)
- [Quickstart](docs/quickstart.md)
- [Core concepts](docs/concepts.md)
- [Policy model](docs/policy-model.md)
- [Architecture](docs/architecture.md)
- [Agent Plugin](docs/agent-plugin.md)
- [MCPB / Smithery local bundle](docs/mcpb.md)
- [Registry submissions (manual)](REGISTRY_SUBMISSIONS.md)
- [Adapters](docs/adapters.md)
- [Writing custom evaluators](docs/custom-evaluators.md)
- [Benchmarks](docs/benchmarks.md)
- [Security claims](docs/security-claims.md)
- [Threat model](docs/threat-model.md)
- [Limitations](docs/limitations.md)
- [Supply-chain verification](docs/supply-chain.md)

## Contributing

Contribution access is approval-only. Start with a proposal and read
[CONTRIBUTING.md](CONTRIBUTING.md) and
[ARCHMAGE_RANKS.md](ARCHMAGE_RANKS.md). Security-sensitive changes require
private disclosure and tests that demonstrate both the blocked path and the
expected compliant path.

## License

Apache License 2.0. See [LICENSE](LICENSE).
