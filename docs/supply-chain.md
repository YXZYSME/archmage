<!-- YXZYS | saeng-il ai [integration] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# Supply-chain verification

Public releases are designed to include:

- one wheel and one source distribution;
- `SHA256SUMS`;
- an SPDX JSON SBOM;
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

Repeat the command for the source distribution. Add `--format json` to inspect
the returned attestations and their predicate types.

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
