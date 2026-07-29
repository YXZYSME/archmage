from typing import Any, Dict, List, Optional, Sequence

from archmage.runtime.domain import (
    ActionProposal,
    ActorIdentity,
    ApprovalRecord,
    PolicyContext,
    ProposedEffect,
)
from archmage.runtime.exceptions import PolicyViolationError
from archmage.runtime.pdp import PolicyEnforcementPoint

from ._context import AdapterExecutionContext, validate_tool_payload


class AntigravityAdapter:
    _TOOL_SPECS = {
        "multi_replace_file_content": ("TargetFile", "file_write"),
        "run_command": ("Cwd", "shell_command"),
        "view_file": ("AbsolutePath", "file_read"),
        "write_to_file": ("TargetFile", "file_write"),
    }

    def __init__(self, pep: PolicyEnforcementPoint):
        self.pep = pep

    def intercept_tool_call(
        self,
        tool_name: str,
        args: Dict[str, Any],
        context_meta: Dict[str, Any],
        approval_records: Optional[Sequence[ApprovalRecord]] = None,
    ) -> bool:
        """
        Translates Antigravity native tool calls into ActionProposal format
        and routes them through the PEP. Returns True if the action is allowed,
        False or raises an Exception if denied.
        """
        execution_context = AdapterExecutionContext.from_mapping(context_meta)
        validate_tool_payload(tool_name, args)
        _path_field, effect_type = self._tool_spec(tool_name)
        target_paths = self._extract_paths(tool_name, args)

        action = ActionProposal(
            task_id=execution_context.task_id,
            actor=ActorIdentity(actor_id=execution_context.actor_id, actor_type="agent"),
            operation=tool_name,
            tool=tool_name,
            arguments=args,
            target_paths=target_paths,
            requested_side_effects=[
                ProposedEffect(effect_type=effect_type, target=tool_name, payload=args)
            ],
            repository_revision=execution_context.repository_revision,
            environment=execution_context.environment,
        )

        context = PolicyContext(
            workspace=execution_context.workspace,
            environment=execution_context.environment,
        )

        try:
            if approval_records is None:
                verdict = self.pep.intercept(action, context)
            else:
                verdict = self.pep.intercept(
                    action,
                    context,
                    approval_records=approval_records,
                )
        except PolicyViolationError as e:
            raise PermissionError(
                f"Action {tool_name} was denied by ARCHMAGE policy engine. Verdict: DENY - {e}"
            ) from e

        if verdict in ("DENY", "ESCALATE"):
            raise PermissionError(
                f"Action {tool_name} was denied by ARCHMAGE policy engine. Verdict: {verdict}"
            )

        return verdict in ("ALLOW", "ALLOW_WITH_OBLIGATIONS")

    def _extract_paths(self, tool: str, args: Dict[str, Any]) -> List[str]:
        path_field, _effect_type = self._tool_spec(tool)
        value = args.get(path_field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{tool} requires a non-empty string argument '{path_field}'")
        return [value]

    def _tool_spec(self, tool: str) -> tuple[str, str]:
        try:
            return self._TOOL_SPECS[tool]
        except KeyError as error:
            raise ValueError(
                f"unregistered tool '{tool}' is denied by the Antigravity adapter"
            ) from error
