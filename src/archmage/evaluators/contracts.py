import ast

from archmage.runtime.domain import (
    ActionProposal,
    Obligation,
    PolicyContext,
    PolicyVerdict,
    RepairInstruction,
    VerdictDecision,
)
from archmage.runtime.evaluators import BaseEvaluator


class ContractDepthEvaluator(BaseEvaluator):
    """
    Enforces Law 1 (Interface Depth).
    Checks public method count and parameter count on proposed Python files using AST.
    Emits REPAIR with refactor instruction if DepthScore is below threshold.
    """

    def __init__(self, max_public_methods: int = 15, max_params_per_method: int = 6):
        self.max_public_methods = max_public_methods
        self.max_params_per_method = max_params_per_method

    def evaluate(
        self, action: ActionProposal, context: PolicyContext, action_digest: str
    ) -> PolicyVerdict:
        code_content = (
            action.arguments.get("CodeContent")
            or action.arguments.get("code")
            or action.arguments.get("content")
        )

        if not code_content:
            return self._allow(action, action_digest, "POL-CONTRACT-DEPTH-01", [1])

        try:
            tree = ast.parse(code_content)
        except SyntaxError:
            return self._allow(action, action_digest, "POL-CONTRACT-DEPTH-01", [1])

        public_methods = 0
        over_param_methods = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):
                    public_methods += 1
                    args_count = len(
                        [arg for arg in node.args.args if arg.arg not in ("self", "cls")]
                    )
                    if args_count > self.max_params_per_method:
                        over_param_methods.append((node.name, args_count))

        depth_violation = False
        findings = []

        if public_methods > self.max_public_methods:
            depth_violation = True
            findings.append(
                f"Too many public methods ({public_methods} > {self.max_public_methods})"
            )

        if over_param_methods:
            depth_violation = True
            findings.append(
                "Methods exceed max parameter threshold "
                f"({self.max_params_per_method}): {over_param_methods}"
            )

        if depth_violation:
            return PolicyVerdict(
                decision=VerdictDecision.REPAIR,
                policy_id="POL-CONTRACT-DEPTH-01",
                policy_version="1.0.0",
                law_ids=[1],
                severity="medium",
                confidence=1.0,
                actor_id=action.actor.actor_id if action.actor else "unknown",
                task_id=action.task_id,
                action_digest=action_digest,
                artifacts=action.target_paths,
                finding="; ".join(findings),
                repair=RepairInstruction(
                    operation="refactor_interface_depth",
                    required_fields=["extract_subcomponent", "reduce_parameter_count"],
                ),
            )

        return self._allow(action, action_digest, "POL-CONTRACT-DEPTH-01", [1])


class ContractFirstEvaluator(BaseEvaluator):
    """
    Enforces Law 3 (Interface-First Development).
    Checks that any proposed function body has a corresponding docstring + type annotations
    before implementation begins. Emits ALLOW_WITH_OBLIGATIONS if missing.
    """

    def evaluate(
        self, action: ActionProposal, context: PolicyContext, action_digest: str
    ) -> PolicyVerdict:
        code_content = (
            action.arguments.get("CodeContent")
            or action.arguments.get("code")
            or action.arguments.get("content")
        )

        if not code_content:
            return self._allow(action, action_digest, "POL-CONTRACT-FIRST-01", [3])

        try:
            tree = ast.parse(code_content)
        except SyntaxError:
            return self._allow(action, action_digest, "POL-CONTRACT-FIRST-01", [3])

        missing_docstrings = []
        missing_type_annotations = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                has_docstring = ast.get_docstring(node) is not None
                if not has_docstring:
                    missing_docstrings.append(node.name)

                has_return_anno = node.returns is not None
                args_without_anno = [
                    arg.arg
                    for arg in node.args.args
                    if arg.arg not in ("self", "cls") and arg.annotation is None
                ]
                if not has_return_anno or args_without_anno:
                    missing_type_annotations.append(node.name)

        if missing_docstrings or missing_type_annotations:
            return PolicyVerdict(
                decision=VerdictDecision.ALLOW_WITH_OBLIGATIONS,
                policy_id="POL-CONTRACT-FIRST-01",
                policy_version="1.0.0",
                law_ids=[3],
                severity="medium",
                confidence=1.0,
                actor_id=action.actor.actor_id if action.actor else "unknown",
                task_id=action.task_id,
                action_digest=action_digest,
                artifacts=action.target_paths,
                finding=(
                    "Missing interface declarations in proposed functions "
                    f"(Missing docstring: {missing_docstrings}; "
                    f"Missing type annotations: {missing_type_annotations})."
                ),
                obligations=[
                    Obligation(type="add_type_annotations_and_docstrings", required_before="merge")
                ],
            )

        return self._allow(action, action_digest, "POL-CONTRACT-FIRST-01", [3])
