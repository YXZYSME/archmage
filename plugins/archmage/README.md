<!-- YXZYS | saeng-il ai [integration] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# ARCHMAGE Claude Code plugin

This directory is the Claude Code plugin listed by the repository marketplace at
`.claude-plugin/marketplace.json`. It is **not** the Agent Plugins 1.0.0 ZIP
template in `agent-plugin/`, and it is **not** an MCPB bundle.

| Artifact | What it is | What it is not |
|---|---|---|
| `plugins/archmage/` | Claude Code plugin (marketplace + PreToolUse + local stdio MCP) | Agent Plugin ZIP, MCPB |
| `agent-plugin/` | Agent Plugins 1.0.0 build template | Claude Code plugin, MCPB |
| MCPB | Claude Desktop / Smithery local bundle (see `docs/mcpb.md`) | Claude Code plugin, Agent Plugin ZIP |

Install after this repository is available as a marketplace:

```text
/plugin marketplace add YXZYSME/archmage
/plugin install archmage@archmage
```

Or from a CLI:

```bash
claude plugin marketplace add YXZYSME/archmage
claude plugin install archmage@archmage
```

The bundled MCP server expects `archmage-ai` on the local Python path:

```bash
python -m pip install archmage-ai
```

`.mcp.json` starts `python -m archmage.mcp` with `ARCHMAGE_AUDIT_LOG` pointing
at a plugin-local JSONL file. There is no hosted URL.

## PreToolUse mapping

`hooks/pretooluse.py` evaluates Write, Edit, MultiEdit, NotebookEdit, and Bash
proposals through the same default PDP used by native integrations. It maps
verdicts to Claude Code `permissionDecision` values:

| ARCHMAGE verdict | `permissionDecision` | Why |
|---|---|---|
| `ALLOW` | `allow` | The evaluated action is compliant. |
| `DENY` | `deny` | Fail-closed block. |
| `ESCALATE` | `ask` | A human or external authority must decide. |
| `REPAIR` | `deny` | Fail-closed; the proposal must change before dispatch. |
| `ALLOW_WITH_OBLIGATIONS` | `ask` | Not auto-allow. Claude Code can collect the human/host obligation (including `explicit_approval` on shell commands). |
| Import, parse, or evaluation failure | `deny` | Fail-closed. Missing `archmage`, workspace, or immutable git revision cannot proceed. |

This matches ARCHMAGE's documented fail-closed default: only a clean `ALLOW`
auto-permits execution. `ask` is still not execution. It is the host's
human-in-the-loop gate for `ESCALATE` and unfulfilled obligations.

The hook is an adapter. It does not replace `PolicyEnforcementPoint`, create a
second policy implementation, or sandbox the operating system. Installing the
plugin does not intercept tool calls that never pass through Claude Code
PreToolUse.
