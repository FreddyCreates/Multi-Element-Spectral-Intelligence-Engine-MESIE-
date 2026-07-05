"""HERMES fleet registry — 12 Cloudflare Workers from sovereign colony fleet."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from mesie.version_info import HERMES_VERSION, MESIE_VERSION

PROTOCOL = "HERMES-FLEET/1.0"
NOVA_PROTOCOL = "NOVA-PROTOCOL-CLEAN-INTERNET/1.0"
BRAND = "ItsnotAILabs"


@dataclass(frozen=True)
class HermesWorker:
    worker_id: str
    slot: str
    title: str
    category: str
    route: str
    operations: Tuple[str, ...]
    generates: Tuple[str, ...]
    processor_proxy: str
    description: str


HERMES_WORKERS: List[HermesWorker] = [
    HermesWorker(
        "hermes-ingest",
        "H01",
        "Ingest Envelope",
        "ingestion",
        "/hermes/ingest",
        ("receive", "normalize", "receipt"),
        ("ingest_envelope.json",),
        "POST /processor/embed",
        "AI data ingestion — spectral records, JSONL, federated envelopes.",
    ),
    HermesWorker(
        "hermes-embed",
        "H02",
        "Edge Embed Proxy",
        "embedding",
        "/hermes/embed",
        ("encode", "batch_encode", "phi_kernel"),
        ("embed_package.json",),
        "POST /processor/compute/encode",
        "ST-φ edge embed — sub-ms, no torch, routes to :8750.",
    ),
    HermesWorker(
        "hermes-validate",
        "H03",
        "Spectral Validate",
        "quality",
        "/hermes/validate",
        ("schema_check", "level_gate"),
        ("validate_rules.json",),
        "POST /processor/validate",
        "MESIE schema levels 1–6 — quality gate before ingest.",
    ),
    HermesWorker(
        "hermes-match",
        "H04",
        "ANN Match Lane",
        "retrieval",
        "/hermes/match",
        ("top_k", "cosine", "lsh"),
        ("match_index.json",),
        "POST /processor/match",
        "Fast spectral ANN — band-sign LSH retrieval at edge.",
    ),
    HermesWorker(
        "hermes-envelope",
        "H05",
        "Federated Envelope",
        "federation",
        "/hermes/envelope",
        ("wrap", "unwrap", "route"),
        ("federated_envelope.schema.json",),
        "POST /processor/grok/worker",
        "MCP federated envelope — cross-AI tool invoke at edge.",
    ),
    HermesWorker(
        "hermes-icp-cli",
        "H06",
        "ICP CLI Forge",
        "icp",
        "/hermes/icp",
        ("dfx_deploy", "canister_map", "bridge_sync"),
        ("HERMES_ICP_CLI.json", "deploy.sh"),
        "GET /processor/federation/status",
        "Generates ICP CLI manifests — sovereign canister deploy scripts.",
    ),
    HermesWorker(
        "hermes-wrangler",
        "H07",
        "Wrangler Forge",
        "deploy",
        "/hermes/wrangler",
        ("toml", "routes", "vars"),
        ("wrangler.toml", "wrangler.hermes.toml"),
        "GET /processor/hermes",
        "Auto-generates wrangler.toml for all 12 workers + bindings.",
    ),
    HermesWorker(
        "hermes-sdk-pack",
        "H08",
        "SDK Packager",
        "sdk",
        "/hermes/sdk",
        ("bundle", "version", "export"),
        ("HERMES_SDK_MANIFEST.json", "hermes-sdk.zip"),
        "GET /processor/models",
        "One-shot SDK pack — MAESI + HERMES + ingest clients.",
    ),
    HermesWorker(
        "hermes-json-corpus",
        "H09",
        "JSON Corpus Pack",
        "large_data",
        "/hermes/corpus",
        ("harvest", "slice", "export_jsonl"),
        ("CORPUS_SLICE.jsonl", "CORPUS_INDEX.json"),
        "POST /processor/platform/producer-pipeline/invoke",
        "932+ record corpus packages for AI ingesting pipelines.",
    ),
    HermesWorker(
        "hermes-nova-pulse",
        "H10",
        "NOVA Pulse",
        "nova",
        "/hermes/nova",
        ("career_pulse", "runtime_tick", "lrc_mint"),
        ("NOVA_PULSE.json",),
        "GET /processor/grok/protocol",
        "NOVA 70-career pulse — never-stop runtime at edge.",
    ),
    HermesWorker(
        "hermes-clean-feed",
        "H11",
        "Clean Internet Feed",
        "clean_internet",
        "/hermes/clean",
        ("filter", "sanitize", "provenance"),
        ("clean_feed_rules.json",),
        "GET /processor/hermes/nova-protocol",
        "NOVA PROTOCOL clean feed — recursive AI safe ingestion lane.",
    ),
    HermesWorker(
        "hermes-deploy-shot",
        "H12",
        "One-Shot Deploy",
        "execution",
        "/hermes/deploy",
        ("pack", "verify", "ship"),
        ("DEPLOY_SHOT.json", "deploy.ps1", "deploy.sh"),
        "POST /processor/hermes/forge",
        "Ready-to-run execution interface — wrangler + ICP + SDK one shot.",
    ),
]


def worker_by_id(worker_id: str) -> Optional[HermesWorker]:
    for w in HERMES_WORKERS:
        if w.worker_id == worker_id:
            return w
    return None


def hermes_manifest() -> Dict[str, Any]:
    return {
        "protocol": PROTOCOL,
        "nova_protocol": NOVA_PROTOCOL,
        "mesie_version": MESIE_VERSION,
        "hermes_version": HERMES_VERSION,
        "brand": BRAND,
        "worker_count": len(HERMES_WORKERS),
        "third_party_inference": False,
        "icp_embedded": True,
        "cloudflare_fleet": True,
        "tagline": "Clean internet for AI — execution interface for recursive NeuroAI + MicroAI + Web3",
        "workers": [
            {
                "worker_id": w.worker_id,
                "slot": w.slot,
                "title": w.title,
                "category": w.category,
                "route": w.route,
                "operations": list(w.operations),
                "generates": list(w.generates),
                "processor_proxy": w.processor_proxy,
                "description": w.description,
            }
            for w in HERMES_WORKERS
        ],
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }