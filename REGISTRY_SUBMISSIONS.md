<!-- YXZYS | saeng-il ai [integration] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# Registry submissions (draft — do not publish from this checkout)

This file is a maintainer runbook. Every command and paste block below is for
**you** to run or submit later. Do not run `mcp-publisher login`,
`mcp-publisher publish`, Smithery publish, Glama submit, or any other
registry publish from CI or from an agent session.

Official MCP namespace: `io.github.YXZYSME/archmage`

PyPI ownership proof is a README marker, **not** an `mcpName` field in
`pyproject.toml` (`mcpName` is npm-only). The marker in `README.md` is:

```html
<!-- mcp-name: io.github.YXZYSME/archmage -->
```

Re-upload `archmage-ai` to PyPI after that marker is on the default branch so
the published package description contains `mcp-name: io.github.YXZYSME/archmage`
(space after the colon is required).

---

## 1. Official MCP Registry

- Submit URL / API: https://registry.modelcontextprotocol.io
- Docs: https://modelcontextprotocol.io/registry
- Package types / PyPI proof: https://modelcontextprotocol.io/registry/package-types
- Schema used by `server.json`: https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json

`server.json` is already in the repository root. Do **not** invent `mcpName` in
`pyproject.toml`. Run these commands yourself after the README marker is live
on PyPI:

```bash
# Install mcp-publisher (Homebrew)
brew install mcp-publisher

# Or install the latest pre-built binary (macOS/Linux)
curl -L "https://github.com/modelcontextprotocol/registry/releases/latest/download/mcp-publisher_$(uname -s | tr '[:upper:]' '[:lower:]')_$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/').tar.gz" | tar xz mcp-publisher
sudo mv mcp-publisher /usr/local/bin/

mcp-publisher --help

# Optional: only if you need a fresh template. Prefer the committed server.json.
# mcp-publisher init

# Authenticate as GitHub user YXZYSME (opens a browser; do not run in CI)
mcp-publisher login github

# Publish the committed server.json (do not run until PyPI README contains mcp-name)
mcp-publisher publish
```

Reminder: bump or re-upload PyPI after the README marker lands so the PyPI
description includes `mcp-name: io.github.YXZYSME/archmage`. Registry
validation searches that exact string in the package README.

---

## 2. Glama

- Submit: https://glama.ai/mcp/servers (Add MCP Server)
- Claim: open the resulting server page and claim via GitHub auth
- Docs: https://glama.ai/blog/2025-07-08-what-is-glamajson

`glama.json` is already at the repository root:

```json
{
  "$schema": "https://glama.ai/mcp/schemas/server.json",
  "maintainers": ["YXZYSME"]
}
```

Submit paste:

```text
GitHub repository: https://github.com/YXZYSME/archmage
Display name: ARCHMAGE
Short description: Deterministic pre-execution control for coding-agent actions.
```

After Glama indexes and you claim the listing, add one of these badges to
README (do not add them until the Glama page exists):

```markdown
[![YXZYSME/archmage MCP server](https://glama.ai/mcp/servers/YXZYSME/archmage/badges/score.svg)](https://glama.ai/mcp/servers/YXZYSME/archmage)
```

```markdown
[![YXZYSME/archmage MCP server](https://glama.ai/mcp/servers/YXZYSME/archmage/badges/card.svg)](https://glama.ai/mcp/servers/YXZYSME/archmage)
```

If Glama assigns a different path than `YXZYSME/archmage`, replace the path in
both the image and the link.

---

## 3. Smithery (path B — MCPB / local bundle)

- Publish docs: https://www.smithery.ai/docs/build/publish
- MCPB tooling: https://github.com/anthropics/mcpb
- Do **not** publish a hosted Streamable HTTP URL.
- Do **not** create `smithery.yaml` unless a future MCPB authoring guide
  requires it. Current Smithery URL/MCPB docs do not.

Exact maintainer steps are in `docs/mcpb.md`. Short form:

```bash
npm install -g @anthropic-ai/mcpb
# in a dedicated MCPB working directory:
mcpb init
mcpb validate
mcpb pack
smithery mcp publish ./dist/archmage.mcpb -n YXZYSME/archmage
```

---

## 4. mcp.so

- Directory: https://mcp.so/
- Submit form / nav Submit control on https://mcp.so/
- Community inbox: https://github.com/chatmcp/mcpso/issues/1

Form / issue comment paste (do not post until you are ready):

```markdown
## ARCHMAGE

- GitHub: https://github.com/YXZYSME/archmage
- PyPI: https://pypi.org/project/archmage-ai/
- Docs: https://archmage.saengil.ai/
- Official MCP name: `io.github.YXZYSME/archmage`
- Transport: local stdio (no hosted URL)
- Install: `python -m pip install archmage-ai`
- Run: `ARCHMAGE_AUDIT_LOG=$HOME/.archmage/audit.jsonl python -m archmage.mcp`
- Alternate command: `archmage-mcp` (same audit-log requirement)
- Description: Deterministic pre-execution control for coding-agent actions.
- Features: evaluate_action, acknowledge_obligations, reconcile_result, inspect_policy
```

---

## 5. PulseMCP

- Submit page: https://www.pulsemcp.com/submit
- Status as of 2026-09: submissions and listing changes are **paused** while
  PulseMCP rebuilds its directory pipeline. Do not expect a working form.
- When operating normally, PulseMCP ingests from the Official MCP Registry.
  Publish `server.json` there first; no separate PulseMCP submission is
  required unless they reopen a manual form.

---

## 6. agentskills.io / skills.sh

- Spec: https://agentskills.io/specification
- Listing / telemetry: https://skills.sh/
- There is no submission form. skills.sh lists installs performed through
  the skills CLI.

Install command for telemetry listing:

```bash
npx skills add YXZYSME/archmage
```

Expected listing URL after installs are counted:

```text
https://skills.sh/YXZYSME/archmage
```

Root `SKILL.md` was checked against the Agent Skills spec: required `name` and
`description` are present; `name: archmage` is kebab-case and matches this
repository's distribution model at repo root; optional `license`,
`compatibility`, and string-to-string `metadata` keys are valid. No frontmatter
key rename was required.

---

## 7. VoltAgent / awesome-agent-skills

- List: https://github.com/VoltAgent/awesome-agent-skills
- Defer the PR if public usage is still immature. Their contributing note
  asks for community-adopted skills, not brand-new unused ones.

Prepared PR blurb (description ≤ 10 words):

```text
- [archmage](https://github.com/YXZYSME/archmage) - Deterministic pre-execution policy for coding agents.
```

PR body paste:

```markdown
Add ARCHMAGE to the skills list.

Description: Deterministic pre-execution policy for coding agents.

Install: `npx skills add YXZYSME/archmage` or `python -m pip install archmage-ai`

This PR is deferred until there is public usage evidence, per the list's
community-adoption bar.
```

---

## 8. punkpeye / awesome-mcp-servers

- List: https://github.com/punkpeye/awesome-mcp-servers
- Submit Glama first, claim the listing, then open a one-server PR.

README line (Security / 🏠 local, after Glama exists):

```markdown
- [YXZYSME/archmage](https://github.com/YXZYSME/archmage) 🐍 🏠 - Deterministic pre-execution control for coding-agent actions. [![YXZYSME/archmage MCP server](https://glama.ai/mcp/servers/YXZYSME/archmage/badges/score.svg)](https://glama.ai/mcp/servers/YXZYSME/archmage)
```

---

## 9. systempromptio / awesome-ai-agent-governance

- List: https://github.com/systempromptio/awesome-ai-agent-governance
- Suggested section: Claude Code and MCP Governance (also fits Open-Source
  Governance Toolkits).

Issue / PR text. **Disclose authorship:** you are the ARCHMAGE maintainer.

```markdown
## Add ARCHMAGE (authorship disclosed)

I am the maintainer of ARCHMAGE (`YXZYSME/archmage`) and am proposing this
first-party listing.

Suggested entry under **Claude Code and MCP Governance**:

- [ARCHMAGE](https://github.com/YXZYSME/archmage) - Deterministic pre-execution policy for coding-agent actions. Python PDP/PEP, local stdio MCP (`archmage-ai` / `python -m archmage.mcp`), and a Claude Code PreToolUse plugin that maps ALLOW/DENY/ESCALATE/REPAIR/ALLOW_WITH_OBLIGATIONS to allow, deny, or ask. Apache-2.0.

I will not open this PR until the Official MCP Registry and Glama listings
exist, unless a maintainer of this list prefers an earlier docs-only entry.
```

---

## 10. Claude Code marketplace

No third-party registration. Users add this repository as a marketplace:

```text
/plugin marketplace add YXZYSME/archmage
/plugin install archmage@archmage
```

```bash
claude plugin marketplace add YXZYSME/archmage
claude plugin install archmage@archmage
```

Requires `python -m pip install archmage-ai` on the same machine so
`python -m archmage.mcp` and the PreToolUse hook can import `archmage`.

See `plugins/archmage/README.md`.
