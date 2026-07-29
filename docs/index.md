<!-- YXZYS | saeng-il ai [development] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# ARCHMAGE

ARCHMAGE is a Python policy runtime for evaluating coding-agent actions before a
host adapter executes them.

It standardizes a proposed action, computes a stable digest, evaluates declared
policies, and returns a typed decision. The host remains responsible for making
that decision authoritative at the tool boundary.

## Start here

1. Follow the [quickstart](quickstart.md).
2. Read the [concepts](concepts.md) and [security limitations](limitations.md).
3. Choose an [adapter](adapters.md).
4. Run the [benchmark suite](benchmarks.md) against your integration.

## Public wedge

The initial release focuses on deterministic pre-execution control for
coding-agent file and command proposals. It does not claim general model safety,
prompt moderation, or operating-system isolation.
