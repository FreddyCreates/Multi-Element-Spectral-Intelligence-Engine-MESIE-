/**
 * HERMES H06 — ICP CLI Forge
 * NOVA PROTOCOL · ItsnotAILabs · hermes-icp-cli
 */
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    };
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: cors });
    }
    const meta = {
      protocol: "HERMES-FLEET/1.0",
      worker_id: "hermes-icp-cli",
      slot: "H06",
      category: "icp",
      operations: ['dfx_deploy', 'canister_map', 'bridge_sync'],
      processor_proxy: "GET /processor/federation/status",
      third_party_inference: false,
    };
    if (url.pathname === "/health") {
      return Response.json({ ok: true, ...meta }, { headers: cors });
    }
    const edge = env.MESIE_PROCESSOR_URL || "http://127.0.0.1:8750";
    try {
      const body = request.method === "POST" ? await request.text() : null;
      const proxyPath = routeToProcessor("hermes-icp-cli");
      const target = edge + proxyPath;
      const init = {
        method: request.method === "GET" ? "GET" : "POST",
        headers: { "Content-Type": "application/json" },
      };
      if (body) init.body = body;
      const upstream = await fetch(target, init);
      const data = await upstream.json();
      return Response.json({
        ok: true,
        hermes: meta,
        upstream: data,
      }, { headers: cors });
    } catch (err) {
      return Response.json({
        ok: false,
        hermes: meta,
        error: String(err),
        offline_pack: "deliverables/hermes/packages/hermes-icp-cli.json",
      }, { status: 502, headers: cors });
    }
  },
};

function routeToProcessor(workerId) {
  const routes = {
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
  };
  return routes[workerId] || "/processor/hermes";
}
