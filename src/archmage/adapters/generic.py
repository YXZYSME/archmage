from typing import Any, Dict, List, Optional, Sequence

from archmage.runtime.domain import (
    ActionProposal,
    ActorIdentity,
    ApprovalRecord,
    PolicyContext,
    ProposedEffect,
)
from archmage.runtime.pdp import PolicyEnforcementPoint

from ._context import AdapterExecutionContext, validate_tool_payload


class GenericAdapter:
    _TOOL_EFFECT_TYPES = {
        "run_command": "shell_command",
        "write_to_file": "file_write",
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
        # Translate IDE/Runtime specific format into ActionProposal
        execution_context = AdapterExecutionContext.from_mapping(context_meta)
        validate_tool_payload(tool_name, args)
        effect_type = self._effect_type(tool_name)
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

        if approval_records is None:
            verdict = self.pep.intercept(action, context)
        else:
            verdict = self.pep.intercept(
                action,
                context,
                approval_records=approval_records,
            )

        # Return True if allowed to proceed, False otherwise
        return verdict in ("ALLOW", "ALLOW_WITH_OBLIGATIONS")

    def _extract_paths(self, tool: str, args: Dict[str, Any]) -> List[str]:
        field = "TargetFile" if tool == "write_to_file" else "Cwd"
        value = args.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{tool} requires a non-empty string argument '{field}'")
        return [value]

    def _effect_type(self, tool: str) -> str:
        try:
            return self._TOOL_EFFECT_TYPES[tool]
        except KeyError as error:
            raise ValueError(
                f"unregistered tool '{tool}' is denied by the generic adapter"
            ) from error
