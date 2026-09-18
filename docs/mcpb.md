<!-- YXZYS | saeng-il ai [integration] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# MCPB (local stdio bundle)

ARCHMAGE's Smithery and Claude Desktop install path is **path B**: a local
MCPB / stdio bundle that runs on the user's machine. This repository does
**not** ship a hosted Streamable HTTP server, and it does not include
`smithery.yaml`. Current Smithery publish docs do not require `smithery.yaml`
for URL or MCPB releases.

## Three different distribution artifacts

| Artifact | Path | Consumer | How it is built |
|---|---|---|---|
| Python package | PyPI `archmage-ai` | Library + `archmage-mcp` / `python -m archmage.mcp` | `python -m build` |
| Agent Plugin ZIP | GitHub release asset | Agent Plugins 1.0.0 hosts | `scripts/build_agent_plugin.py` |
| Claude Code plugin | `plugins/archmage/` | `/plugin marketplace add YXZYSME/archmage` | Committed tree; no ZIP build |
| MCPB | Not built in-repo yet | Claude Desktop, Smithery local install | Anthropic `mcpb` CLI (this page) |

Agent Plugin ZIP ≠ MCPB ≠ Claude Code plugin. Do not upload the Agent Plugin
ZIP to Smithery or the Official MCP Registry as if it were an MCPB.

## What an ARCHMAGE MCPB must contain

An MCPB is a zip archive with a `manifest.json` and a local stdio server.
For ARCHMAGE that server is the existing Python entry point:

```bash
python -m archmage.mcp
# or, after pip install archmage-ai:
archmage-mcp
```

Both require `ARCHMAGE_AUDIT_LOG` or `--audit-log`. Bundle that path through
MCPB user configuration, not a hardcoded machine path.

Official authoring references (placeholders for the current Anthropic docs):

- MCPB overview and CLI: https://github.com/anthropics/mcpb
- Manifest specification: https://github.com/anthropics/mcpb/blob/main/MANIFEST.md
- Claude Desktop extensions / MCPB: https://www.anthropic.com/engineering/desktop-extensions
- Smithery local MCPB publish: https://www.smithery.ai/docs/build/publish

## Maintainer commands (do not run in CI)

Install the MCPB CLI, then author and pack a bundle in a dedicated working
directory that contains the stdio server files you intend to distribute:

```bash
npm install -g @anthropic-ai/mcpb
# from the MCPB working directory:
mcpb init
mcpb validate
mcpb pack
```

`mcpb init` writes `manifest.json`. For a Python / uv runtime, follow the
current MCPB Python or `server.type = "uv"` examples in the Anthropic repo
(`examples/hello-world-uv` when present). Point `server.mcp_config` at
`python -m archmage.mcp` or `archmage-mcp`, and declare `ARCHMAGE_AUDIT_LOG`
as required user configuration.

Suggested local names (not created by this repository):

```text
dist/archmage.mcpb
```

Validate the archive before any upload. Compute a SHA-256 if you later list
the MCPB on the Official MCP Registry (`registryType: mcpb`):

```bash
openssl dgst -sha256 dist/archmage.mcpb
```

## Smithery publish (path B, local bundle)

Smithery distributes a pre-built `.mcpb` that clients download and run
locally. After `mcpb pack` succeeds, the maintainer publishes the bundle
themselves:

```bash
# Install the Smithery CLI using the current Smithery docs, then:
smithery mcp publish ./dist/archmage.mcpb -n YXZYSME/archmage
```

Do not publish a hosted URL. Do not add a Streamable HTTP server to satisfy
Smithery path A.

If the Smithery CLI command names change, prefer the commands printed by
https://www.smithery.ai/docs/build/publish over this page.

## Claude Desktop sideload

Claude for macOS and Windows can open a `.mcpb` file and show an
installation dialog. That sideload path is the same local stdio server,
not a remote endpoint.

## Cross-links

- Agent Plugin ZIP build and verify: [agent-plugin.md](agent-plugin.md)
- Registry paste text and remaining manual submit steps: `REGISTRY_SUBMISSIONS.md` at the repository root
- Claude Code marketplace plugin: `plugins/archmage/README.md`
