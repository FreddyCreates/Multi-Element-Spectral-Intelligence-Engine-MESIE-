"""OpenAI-style tool schemas for enterprise copilots — sovereign local MESIE + SOLUS."""

from __future__ import annotations

from typing import Any, Dict, List


def build_enterprise_tool_schemas() -> List[Dict[str, Any]]:
    """Tool definitions for on-prem agent runtimes (OpenAI, Anthropic, custom)."""
    return [
        {
            "type": "function",
            "function": {
                "name": "mesie_agent_memory_recall",
                "description": "Recall spectral agent memory: corpus neighbors + prior session turns. Fully local.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "record": {"type": "object", "description": "Spectral JSON record"},
                        "session_id": {"type": "string", "description": "Copilot session id"},
                        "top_k": {"type": "integer", "default": 5},
                    },
                    "required": ["record"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_solus_reason",
                "description": "SOLUS sovereign local reasoning on a spectrum — Logic Prover + Pattern Forge.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "record": {"type": "object", "description": "Spectral JSON record"},
                        "theorem": {"type": "string", "description": "Optional logic statement"},
                    },
                    "required": ["record"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_enterprise_copilot_cycle",
                "description": "Full enterprise AI cycle: validate → embed → match → SOLUS memory → agent recall.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "record": {"type": "object"},
                        "session_id": {"type": "string", "default": "default"},
                        "candidate": {"type": "object", "description": "Optional match candidate"},
                    },
                    "required": ["record"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_validate_spectrum",
                "description": "Validate spectral JSON against MESIE schema.",
                "parameters": {"type": "object", "properties": {"record": {"type": "object"}}, "required": ["record"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_match_spectra",
                "description": "Compare two spectra and return composite similarity.",
                "parameters": {
                    "type": "object",
                    "properties": {"reference": {"type": "object"}, "candidate": {"type": "object"}},
                    "required": ["reference", "candidate"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_vault_recall",
                "description": "Recall embedded minted tokens from sovereign vault — reuse prior work.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "results": {"type": "object"},
                        "workflow": {"type": "object"},
                        "composition": {"type": "object"},
                        "top_k": {"type": "integer", "default": 5},
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_vault_status",
                "description": "Sovereign vault status — stored tokens, compound work units.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_verify_receipt_chain",
                "description": "Verify SOLUS computational receipt chain integrity (local HMAC seals).",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_embed_spectrum",
                "description": "Vectorize a spectral record for ANN retrieval.",
                "parameters": {"type": "object", "properties": {"record": {"type": "object"}}, "required": ["record"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_field_route",
                "description": "Route through airgapped world-computer field mesh (aliases: ground, world, leo0, geo).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string", "description": "Source node or alias"},
                        "destination": {"type": "string", "description": "Destination node or alias"},
                        "policy": {"type": "string", "enum": ["shortest", "ladder_only", "orbital_preferred"], "default": "shortest"},
                    },
                    "required": ["source", "destination"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_field_bridge",
                "description": "Bridge a spectrum to the physical frequency field — sovereign access without internet.",
                "parameters": {"type": "object", "properties": {"record": {"type": "object"}}, "required": ["record"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_field_status",
                "description": "Field access mesh status, route table, and health check.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_field_ingest_csv",
                "description": "Ingest a CSV spectral file (frequency,amplitude) into MESIE record + field bridge.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to CSV file"},
                        "record_id": {"type": "string"},
                    },
                    "required": ["path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_field_ingest_udp",
                "description": "Parse a UDP spectral frame payload (JSON or binary) into MESIE record.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "payload_b64": {"type": "string", "description": "Base64-encoded UDP payload"},
                    },
                    "required": ["payload_b64"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_anchor_calibrate",
                "description": "Calibrate field anchors against Schumann/geomag reference libraries.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_swarm_hive_coordinate",
                "description": "Hive mind swarm consensus — N agents threat-fast + route vote.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "record": {"type": "object"},
                        "n_agents": {"type": "integer", "default": 1000},
                    },
                    "required": ["record"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_drone_swarm_coordinate",
                "description": "Decentralized drone swarm: local spectral decisions, gossip consensus, jam/attrition tests.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "record": {"type": "object"},
                        "n_agents": {"type": "integer", "default": 1000},
                        "jam_ground": {"type": "boolean", "default": False},
                        "attrition_rate": {"type": "number", "default": 0.0},
                    },
                    "required": ["record"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_swarm_routing_validate",
                "description": "Validate field mesh routing nervous system — ground/orbital/alias/presets/health.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_swarm_mission_plan",
                "description": "Execute full swarm mission: spectral threat, PSO/MARL tasks, formation, LAN gossip, DTN, drone adapter.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "record": {"type": "object"},
                        "preset_id": {"type": "string", "enum": ["strike", "isr", "ew", "swarm_forge"]},
                        "n_agents": {"type": "integer", "default": 1000},
                        "jam_ground": {"type": "boolean", "default": False},
                    },
                    "required": ["record"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_swarm_task_allocate",
                "description": "Particle swarm or MARL task allocation across swarm agents.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "n_agents": {"type": "integer"},
                        "method": {"type": "string", "enum": ["pso", "marl"]},
                        "spectral_urgency": {"type": "number", "default": 0.8},
                    },
                    "required": ["n_agents"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_swarm_formation",
                "description": "Formation control with collision avoidance and attrition reform.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "n_agents": {"type": "integer", "default": 100},
                        "attrition_rate": {"type": "number", "default": 0.1},
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_mesh_export",
                "description": "Export sovereign mesh bundle (route table + receipts) for LAN peers.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_mesh_peers",
                "description": "List imported sovereign mesh peers on local LAN drop folder.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_domain_catalog",
                "description": "List expanded domain corpus — seismic, power, defense, bio, geomag, libraries.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domains": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_fast_enterprise_cycle",
                "description": "Fast enterprise path: validate→ANN→match→memory→field (no full Octopus).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "record": {"type": "object"},
                        "candidate": {"type": "object"},
                        "session_id": {"type": "string"},
                    },
                    "required": ["record"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_external_benchmark",
                "description": "Run external-style benchmark pack vs MQTT/vector-RAG/cloud-LLM baselines.",
                "parameters": {
                    "type": "object",
                    "properties": {"n_trials": {"type": "integer", "default": 200}},
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_rf_ingest",
                "description": "Live RF adapter — Schumann-band spectral ingest → field bridge (sim or UDP).",
                "parameters": {
                    "type": "object",
                    "properties": {"simulated": {"type": "boolean", "default": True}},
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_production_health",
                "description": "Tier 1 appliance health check — SLA, airgapped, routing, copilot tools.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mesie_specialized_reason",
                "description": "Specialized-general reasoning: domain-tagged spectral analysis across expanded corpus.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "record": {"type": "object"},
                        "domains": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["record"],
                },
            },
        },
    ]