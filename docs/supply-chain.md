<!-- YXZYS | saeng-il ai [integration] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# Supply-chain verification

Public releases are designed to include:

- one wheel and one source distribution;
- one self-contained Agent Plugins 1.0.0 ZIP;
- `SHA256SUMS`;
- separate SPDX JSON SBOMs for Python packages and the Agent Plugin;
- GitHub build-provenance and SBOM attestations;
- revision-bound gold-case, repair-loop, and latency result artifacts;
- PyPI publication through OpenID Connect trusted publishing.

## Verify checksums

```bash
gh release download VERSION --repo YXZYSME/archmage
sha256sum --check SHA256SUMS
```

On macOS, use:

```bash
shasum -a 256 --check SHA256SUMS
```

## Verify GitHub attestations

```bash
gh attestation verify archmage_ai-VERSION-py3-none-any.whl \
  --repo YXZYSME/archmage \
  --signer-workflow YXZYSME/archmage/.github/workflows/release.yml
```

Repeat the command for the source distribution and
`archmage-agent-plugin-VERSION.zip`. Add `--format json` to inspect the returned
attestations and their predicate types.

Benchmark result files are also attested by the release workflow. Verify each
downloaded JSON or Markdown result with the same command and compare its recorded
revision and environment before citing a number.

An attestation binds an artifact to source and workflow provenance. It does not
assert that the artifact is vulnerability-free.

## Inspect the wheel

```bash
python -m zipfile --list archmage_ai-VERSION-py3-none-any.whl
```

The wheel should contain the `archmage` package and declared project data. It
must not install generic top-level packages such as `runtime`, `adapters`,
`skills`, or `tests`.

## Inspect the Agent Plugin

```bash
python -m zipfile --list archmage-agent-plugin-VERSION.zip
python scripts/verify_agent_plugin.py archmage-agent-plugin-VERSION.zip
```

The plugin archive should contain `plugin.json`, `mcp.json`, one exported
`skills/archmage/SKILL.md`, the policy manifest, and a runtime under
`python/archmage`. Its MCP configuration must point `PYTHONPATH` at that bundled
runtime and place the durable audit log under `${PLUGIN_DATA}`.
