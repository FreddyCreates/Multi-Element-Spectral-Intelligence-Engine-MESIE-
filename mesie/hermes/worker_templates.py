"""Cloudflare Worker JS templates — HERMES edge proxies to MESIE processor."""

from __future__ import annotations

from typing import Dict

from mesie.hermes.registry import HermesWorker

PROCESSOR_DEFAULT = "MESIE_PROCESSOR_URL"


def worker_js(w: HermesWorker) -> str:
    """Minimal ES module worker — routes to MESIE edge or handles locally."""
    return f"""/**
 * HERMES {w.slot} — {w.title}
 * NOVA PROTOCOL · ItsnotAILabs · {w.worker_id}
 */
export default {{
  async fetch(request, env, ctx) {{
    const url = new URL(request.url);
    const cors = {{
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }};
    if (request.method === "OPTIONS") {{
      return new Response(null, {{ headers: cors }});
    }}
    const meta = {{
      protocol: "HERMES-FLEET/1.0",
      worker_id: "{w.worker_id}",
      slot: "{w.slot}",
      category: "{w.category}",
      operations: {list(w.operations)!r},
      processor_proxy: "{w.processor_proxy}",
      third_party_inference: false,
    }};
    if (url.pathname === "/health") {{
      return Response.json({{ ok: true, ...meta }}, {{ headers: cors }});
    }}
    const edge = env.{PROCESSOR_DEFAULT} || "http://127.0.0.1:8750";
    try {{
      const body = request.method === "POST" ? await request.text() : null;
      const proxyPath = routeToProcessor("{w.worker_id}");
      const target = edge + proxyPath;
      const init = {{
        method: request.method === "GET" ? "GET" : "POST",
        headers: {{ "Content-Type": "application/json" }},
      }};
      if (body) init.body = body;
      const upstream = await fetch(target, init);
      const data = await upstream.json();
      return Response.json({{
        ok: true,
        hermes: meta,
        upstream: data,
      }}, {{ headers: cors }});
    }} catch (err) {{
      return Response.json({{
        ok: false,
        hermes: meta,
        error: String(err),
        offline_pack: "deliverables/hermes/packages/{w.worker_id}.json",
      }}, {{ status: 502, headers: cors }});
    }}
  }},
}};

function routeToProcessor(workerId) {{
  const routes = {{
    "hermes-ingest": "/processor/embed",
    "hermes-embed": "/processor/compute/encode",
    "hermes-validate": "/processor/status",
    "hermes-match": "/processor/match",
    "hermes-envelope": "/processor/grok/worker",
    "hermes-icp-cli": "/processor/federation/status",
    "hermes-wrangler": "/processor/hermes",
    "hermes-sdk-pack": "/processor/models",
    "hermes-json-corpus": "/processor/platform/producer-pipeline/invoke",
    "hermes-nova-pulse": "/processor/grok/protocol",
    "hermes-clean-feed": "/processor/hermes/nova-protocol",
    "hermes-deploy-shot": "/processor/hermes/forge",
  }};
  return routes[workerId] || "/processor/hermes";
}}
"""


def wrangler_worker_toml(w: HermesWorker, *, account_stub: str = "ITSNOTAILABS_ACCOUNT") -> str:
    return f"""# HERMES {w.slot} — {w.title}
name = "mesie-{w.worker_id}"
main = "index.js"
compatibility_date = "2024-11-01"
workers_dev = true

[vars]
HERMES_WORKER_ID = "{w.worker_id}"
HERMES_SLOT = "{w.slot}"
NOVA_PROTOCOL = "NOVA-PROTOCOL-CLEAN-INTERNET/1.0"
BRAND = "ItsnotAILabs"

# Set at deploy: wrangler secret put MESIE_PROCESSOR_URL
# MESIE_PROCESSOR_URL = "https://your-edge-gateway.example"

[[routes]]
pattern = "{w.route}*"
zone_name = "itsnotailabs.workers.dev"

# account_id = "{account_stub}"
"""


def root_wrangler_toml(workers: list) -> str:
    lines = [
        "# HERMES Fleet — 12 Cloudflare Workers",
        "# NOVA PROTOCOL · Clean Internet for AI · ItsnotAILabs",
        'name = "mesie-hermes-fleet"',
        'compatibility_date = "2024-11-01"',
        "",
    ]
    for w in workers:
        lines.append(f"# {w.slot} {w.worker_id} → {w.route}")
    lines.extend([
        "",
        "[vars]",
        'HERMES_VERSION = "1.0.0"',
        'NOVA_PROTOCOL = "NOVA-PROTOCOL-CLEAN-INTERNET/1.0"',
        'MESIE_VERSION = "1.2.0"',
        "",
    ])
    return "\n".join(lines) + "\n"