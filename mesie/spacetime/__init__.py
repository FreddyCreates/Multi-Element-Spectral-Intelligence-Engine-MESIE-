"""Paper 04 — Embedding Autonomous Agents in Simulated Spacetime."""

from mesie.spacetime.agents import SpatialAgent, default_agent_registry
from mesie.spacetime.eval import run_spacetime_eval
from mesie.spacetime.signals import ClassifiedSignal, SignalTier, classify_signal
from mesie.spacetime.substrate import SimulatedSpacetimeSubstrate, SpacetimeReport
from mesie.spacetime.zones import Zone, default_zones

PAPER04_AUTHORITY = "INTERNAL_RESEARCH"
PAPER04_CLAIM_BOUNDARY = "repo_verified_architecture"

__all__ = [
    "SpatialAgent",
    "default_agent_registry",
    "ClassifiedSignal",
    "SignalTier",
    "classify_signal",
    "Zone",
    "default_zones",
    "SimulatedSpacetimeSubstrate",
    "SpacetimeReport",
    "run_spacetime_eval",
    "PAPER04_AUTHORITY",
    "PAPER04_CLAIM_BOUNDARY",
]