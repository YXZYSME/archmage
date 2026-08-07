---
name: archmage
description: Enforces deterministic pre-execution policy for coding-agent actions and records durable decision evidence. Use before file writes, shell commands, API calls, destructive actions, architecture changes, public interface changes, and other technical work with side effects.
license: Apache-2.0
compatibility: Requires an Agent Plugins client with MCP stdio support and Python 3.9 or newer.
metadata:
  author: YXZYS
  version: "2.0.0"
---

<!-- YXZYS | saeng-il ai [integration] — © YXZYS @ saengil.ai -->

# ARCHMAGE policy enforcement

Use the bundled ARCHMAGE MCP tools as a pre-execution control plane. The MCP server is the
authority for policy decisions; this skill explains the required call sequence.

1. Before any side effect, call `evaluate_action` with the exact actor, operation, tool arguments,
   target paths, requested side effects, repository revision, workspace, and environment.
2. Execute the proposed action only when the response has `executable: true`.
3. Treat `DENY`, `ESCALATE`, `REPAIR`, an unfulfilled obligation, an MCP error, or an unavailable
   server as fail-closed. Do not execute the action.
4. For a non-approval obligation, call `acknowledge_obligations` with the returned action digest and
   then reevaluate the unchanged action. Never acknowledge `explicit_approval`; it requires a
   verified, digest-bound approval record supplied by a trusted host integration.
5. After an allowed action finishes or fails, call `reconcile_result` using the returned
   `action_digest`, the same `task_id`, the actual status, and a concise result summary.
6. Use `inspect_policy` when you need the active evaluator inventory or enforcement capabilities.

Changing any action argument after evaluation creates a different action. Evaluate that changed
action again before execution.

<!-- yxzys:sg:ai -->
