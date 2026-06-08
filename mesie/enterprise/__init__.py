"""Enterprise AI — sovereign agent memory, copilot workflows, local tool schemas."""

from mesie.enterprise.agent_memory import AgentMemoryTurn, EnterpriseAgentMemory
from mesie.enterprise.receipt_chain import (
    ComputationalReceipt,
    ComputationalReceiptChain,
    MintedWorkToken,
    ReceiptChainState,
)
from mesie.enterprise.sovereign_vault import SovereignVault, VaultCompoundState, VaultEntry
from mesie.enterprise.tool_schemas import build_enterprise_tool_schemas

__all__ = [
    "AgentMemoryTurn",
    "ComputationalReceipt",
    "ComputationalReceiptChain",
    "EnterpriseAgentMemory",
    "EnterpriseAICopilot",
    "EnterpriseCycleReport",
    "MintedWorkToken",
    "ReceiptChainState",
    "SovereignVault",
    "VaultCompoundState",
    "VaultEntry",
    "build_enterprise_tool_schemas",
]


def __getattr__(name: str):
    if name in ("EnterpriseAICopilot", "EnterpriseCycleReport"):
        from mesie.enterprise.copilot import EnterpriseAICopilot, EnterpriseCycleReport

        return EnterpriseAICopilot if name == "EnterpriseAICopilot" else EnterpriseCycleReport
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")