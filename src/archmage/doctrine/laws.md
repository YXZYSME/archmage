# ARCHMAGE: Law Operationalization Matrix

This document translates the theoretical **8 Laws of YXZYS** into programmatically observable signals, defining active evaluators, verdicts, and concrete policy candidates for enforcement in agentic environments.

---

## 1. Law Operationalization Matrix

| Law | Invariant | Detectable Signals | Evaluator | Default Verdict | Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Law of Territory (Isolation)** | $WriteAccess(path) == True$ only if $path \subseteq \$WORKSPACE$ | Filesystem writes, `client:write_to_file` targets, `open()` mode 'w' flags in dynamic code. | `FileWriteBoundaryEvaluator` | **DENY** | Absolute target file path, resolved workspace canonical directory path. |
| **2. Law of Lineage (Provenance)** | $HasIdentity(actor) \land HasTrace(action) == True$ | Git commit logs, author email fields, HTTP header span-contexts, parent process IDs. | `ProvenanceEvaluator` | **ESCALATE** | Missing or mismatching caller UUIDs, detached trace context tags. |
| **3. Law of Stewardship (Least Privilege)** | $Capability(action) \subseteq GrantedCapabilities(actor)$ | Triggered tool name, command line parameters, executed binary namespace, active API token. | `CapabilityPrivilegeEvaluator` | **DENY** | Required privilege level vs. active actor clearance profile, command CLI diffs. |
| **4. Law of Concord (Non-Interference)** | $IsolationBarrier(agent_a, agent_b) == True$ | Mutating a file currently locked or owned by a concurrent process, accessing shared databases. | `ConcurrencyBarrierEvaluator` | **ESCALATE** | Process locks, file modification timestamps, active multi-agent session leases. |
| **5. Law of Transparency (Traceability)** | $LogWritten(action) == True$ | Telemetry status codes, Langfuse tracing spans, local enforcer `.md` write results. | `AuditLogger` | **DENY** (if logging fails) | Signed receipt hashes, API gateway connection states, local disk storage availability. |
| **6. Law of Conservatism (Resource Quotas)** | $CumulativeSpend < BudgetLimit$ | Monthly token metrics, CPU/memory cgroup limits, API billing tallies, elapsed execution times. | `ResourceQuotaEvaluator` | **DENY** | Token usage counters, micro-USD billing telemetry, hardware cgroups signals. |
| **7. Law of Verification (Correctness)** | $StaticAnalysis(C) \in Pass \land Tests(C) \in Pass$ | AST analysis node types, unit test exit codes, mypy type checks, lint formatting logs. | `CIValidationEvaluator` | **DENY** | Parse errors, AST traversal logs, pytest results, Black formatter exit codes. |
| **8. Law of Sovereignty (Human Control)** | $RiskLevel \ge 3 \implies HumanApproved == True$ | Voice confirmation tokens, MFA tokens, active interrupt signal detections, prompt approvals. | `HITLApprovalGate` | **ESCALATE** | Human verification cryptographic signature, confirmation logs, interactive stop-word event. |

---

## 2. Detailed Policy Candidates

Below are detailed, operational policy candidates written for each of the 8 Laws to enable immediate automation.

### Law 1: Law of Territory (Isolation)
* **Policy ID**: `POL-TERRITORY-01`
* **Intent**: Prevent an agent from writing to, altering, or deleting files outside of its active task directory.
* **Input**: Target absolute filepath ($F$) and active workspace directory ($W$).
* **Detection Method**: Compare canonicalized absolute path of $F$ against $W$. If $F$ is not a subdirectory of $W$, trigger a boundary exception.
* **Positive Example**: Writing to `/workspace/project/src/main.py` is inside the declared workspace `/workspace/project/`.
* **Negative Example**: Trying to write to `/workspace/.shellrc` or `/etc/hosts` violates the boundary.
* **Known Ambiguity**: Symlink resolution and relative paths (e.g., `../../`) must be fully canonicalized before comparison to avoid bypasses.
* **False-Positive Risk**: High-frequency generation of temporary folders under `/tmp/` that are legitimately required for script execution but are technically outside the active project workspace.
* **Repair Operation**: Intercept path and redirect file output to a `/tmp/archmage-sandbox/` subdirectory associated with the agent UUID.
* **Enforcement Readiness**: Ready for production (Deterministic path comparison).

---

### Law 2: Law of Lineage (Provenance)
* **Policy ID**: `POL-LINEAGE-01`
* **Intent**: Ensure all generated code and commits are strictly associated with a verified agent identity and trace.
* **Input**: Git commit payload (Author, Email, GPG Key) and active session context.
* **Detection Method**: Scan Git configuration variables and commit arguments before git-commit. Verify author email matches the agent's identity template (`agent-{uuid}@saengil.ai`).
* **Positive Example**: Git author set as `EditorAgent <agent-123e4567-e89b-12d3-a456-426614174000@saengil.ai>`.
* **Negative Example**: Git author set as `root <root@localhost>` or `user1 <user1@gmail.com>`.
* **Known Ambiguity**: Merges or rebases that carry third-party commits which have different original author profiles.
* **False-Positive Risk**: Committing changes to open-source libraries where the original code was written by external authors (e.g. retaining author history in submodules).
* **Repair Operation**: Rewrite commit metadata on-the-fly to assign the agent's identity as the committer while keeping original authors in the co-authored block.
* **Enforcement Readiness**: Ready for production (Local Git filter/hooks).

---

### Law 3: Law of Stewardship (Least Privilege)
* **Policy ID**: `POL-STEWARDSHIP-01`
* **Intent**: Block agents from executing high-privilege administrative shell commands.
* **Input**: Proposed command-line string ($CMD$).
* **Detection Method**: Tokenize the command string into its arguments. Compare the command binary and arguments against a regex-based blacklist (e.g., banning `sudo`, `doas`, `chown`, `chmod`).
* **Positive Example**: Executing `pytest tests/` or `npm run build`.
* **Negative Example**: Executing `sudo systemctl restart nginx` or `doas rm -rf /`.
* **Known Ambiguity**: Highly obfuscated shell commands, such as using shell variables or base64 decoding (e.g., `echo "c3VkbyA..." | base64 -d | sh`).
* **False-Positive Risk**: Valid commands containing blacklisted substrings (e.g., a file named `sudo_test.py` or writing about `chmod` in documentation).
* **Repair Operation**: Terminate the active process and strip the execution capabilities from the agent's active shell session.
* **Enforcement Readiness**: Requires LLM judge + Deterministic Regex (Hybrid Gate).

---

### Law 4: Law of Concord (Non-Interference)
* **Policy ID**: `POL-CONCORD-01`
* **Intent**: Avoid split-brain scenarios and file state conflicts in multi-agent environments.
* **Input**: Active session write logs and file lock indicators.
* **Detection Method**: Query active locking leases on workspace files. If Agent $A$ attempts a write on a file currently leased to Agent $B$, halt and queue the action.
* **Positive Example**: Agent $A$ edits `app/models.py` while Agent $B$ edits `app/views.py`.
* **Negative Example**: Agent $A$ attempts to write to `app/config.json` while Agent $B$ is actively editing it.
* **Known Ambiguity**: Non-file state interference, such as concurrent API endpoint calls that modify the same database records.
* **False-Positive Risk**: Stale lock leases left behind by abnormally terminated or crashed agents.
* **Repair Operation**: Introduce a lease timeout (e.g., 60 seconds). If exceeded, perform state validation and break the lock.
* **Enforcement Readiness**: Requires infrastructure-level lock manager (Ready for Staging).

---

### Law 5: Law of Transparency (Traceability)
* **Policy ID**: `POL-TRANSPARENCY-01`
* **Intent**: Enforce the generation and external submission of execution traces for all active agent runs.
* **Input**: Telemetry transmission statuses and enforcer receipts.
* **Detection Method**: Prior to initiating a tool execution, query the connection status to the OpenTelemetry / Langfuse gateway. If unavailable and no offline cache is active, deny tool execution.
* **Positive Example**: Enforcer successfully registers a start span with Langfuse and receives a 201 response.
* **Negative Example**: Network is disconnected and enforcer fails to record a tool interception, letting tool run without logging.
* **Known Ambiguity**: Intermittent network dropouts that happen mid-trace but after pre-tool authorization has already passed.
* **False-Positive Risk**: Blocking critical development work because of temporary remote telemetry server outages.
* **Repair Operation**: Save traces to an encrypted local SQLite database cache (`.archmage_offline.db`) and auto-sync when connection is restored.
* **Enforcement Readiness**: Ready for production (Fallback offline cache pattern).

---

### Law 6: Law of Conservatism (Resource Quotas)
* **Policy ID**: `POL-CONSERVATISM-01`
* **Intent**: Enforce strict budget controls to prevent run-away loops and excessive token spend.
* **Input**: Accumulated session costs ($C_{session}$) and maximum budget ($B_{limit}$).
* **Detection Method**: Track and aggregate token usage and API model costs in real time. If $C_{session} \ge B_{limit}$, block further API calls and tool execution.
* **Positive Example**: Running an optimization loop costing $1.20 against a limit of $5.00.
* **Negative Example**: An infinite loop in a SWE-agent costing $12.50, bypassing a $5.00 safety limit.
* **Known Ambiguity**: Calculating real-time costs when models have complex, dynamic pricing rules (e.g., prompt caching discounts or fluctuating resource costs).
* **False-Positive Risk**: Large, legitimate refactoring tasks on huge codebases that genuinely require high token volumes.
* **Repair Operation**: Prompt human supervisor to dynamically increase budget or manually approve a budget extension.
* **Enforcement Readiness**: Ready for production (Token count and API cost tracking).

---

### Law 7: Law of Verification (Correctness)
* **Policy ID**: `POL-VERIFICATION-01`
* **Intent**: Block committing code that does not pass static syntax analysis or security parsing.
* **Input**: Modified code file string ($C$).
* **Detection Method**: Run Python `ast.parse(C)`. Traverse AST nodes and verify no banned patterns are utilized.
* **Positive Example**: Code with standard function calls and standard library imports.
* **Negative Example**: Code containing `import subprocess` or calling `eval("x + 1")` in a custom indicator module.
* **Known Ambiguity**: Dynamically constructed variables or string obfuscation used to import libraries implicitly.
* **False-Positive Risk**: Writing tests designed explicitly to verify failure cases or dynamic imports, which get flagged by the analyzer.
* **Repair Operation**: Flag code blocks as noncompliant, provide the AST validation report, and suggest secure refactoring alternatives (e.g., using safe parsing instead of `eval`).
* **Enforcement Readiness**: Ready for production (Rigid AST parsers).

---

### Law 8: Law of Sovereignty (Human Control)
* **Policy ID**: `POL-SOVEREIGNTY-01`
* **Intent**: Ensure critical, destructive, or highly anomalous actions obtain explicit human confirmation before execution.
* **Input**: Proposed action risk rating ($R$) and human approval signature token.
* **Detection Method**: If $R \ge 3$ (e.g. installing dependencies, writing outside workspace, or executing dynamic terminal binaries), trigger a HITL escalation event. Require a cryptographically signed approval token.
* **Positive Example**: Agent requests a package install; a pop-up appears on the user's dashboard; the user inputs credentials, and execution resumes.
* **Negative Example**: Agent attempts `pip install` silently in the background and executes code without showing a prompt.
* **Known Ambiguity**: Defining risk levels when a command appears low-risk on the surface but has risky implications based on state.
* **False-Positive Risk**: Constant, repetitive prompting that fatigue the human supervisor, leading them to blindly click "Approve".
* **Repair Operation**: Group low-risk actions into single batch approvals, and restrict Level 3 gates strictly to high-signal actions (e.g., network access or package installs).
* **Enforcement Readiness**: Ready for production (Human-in-the-loop dashboard integration).
