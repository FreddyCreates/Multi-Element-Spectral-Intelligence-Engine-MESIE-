/** MESIE MVP Bridge — web apps → processor :8750 → workers → native backends */
const MESIE_BRIDGE = (() => {
  const BASE = "http://127.0.0.1:8750";
  const UNI = "http://127.0.0.1:8765";
  const CAREER = "http://127.0.0.1:8767";
  const TIMEOUT = 12000;

  const APPS = [
    { id: "platform-hub", label: "Platform", href: "../platform-hub/" },
    { id: "model-hub", label: "Models", href: "../model-hub/" },
    { id: "solus-console", label: "SOLUS", href: "../solus-console/" },
    { id: "auro-studio", label: "Auro", href: "../auro-studio/" },
    { id: "producer-lab", label: "Producer", href: "../producer-lab/" },
    { id: "computing-family", label: "Compute", href: "../computing-family/" },
    { id: "virtual-silicon", label: "VS1", href: "../virtual-silicon/" },
    { id: "reality-engine", label: "Reality", href: "../reality-engine/" },
    { id: "enterprise-4k", label: "Enterprise", href: "../enterprise-4k/" },
    { id: "hermes-fleet", label: "HERMES", href: "../hermes-fleet/" },
    { id: "market-hub", label: "Market", href: "../market-hub/" },
  ];

  const SERVICE_LINKS = {
    "model-hub": "../model-hub/",
    "nova-studio": "../model-hub/#nova",
    "st-phi-encode": "../model-hub/#encode",
    "st-phi-benchmark": "../model-hub/#benchmark",
    "solus-console": "../solus-console/",
    "auro-speak": "../auro-studio/",
    "producer-pipeline": "../producer-lab/",
    "computing-family": "../computing-family/",
    "virtual-silicon": "../virtual-silicon/",
    "reality-engine": "../reality-engine/",
    "enterprise-4k": "../enterprise-4k/",
    "platform-hub": "../platform-hub/",
    "hermes-fleet": "../hermes-fleet/",
  };

  async function fetchJSON(url, opts = {}) {
    const r = await fetch(url, {
      ...opts,
      signal: AbortSignal.timeout(opts.timeout || TIMEOUT),
      headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
    });
    if (!r.ok) throw new Error(`${url} → ${r.status}`);
    return r.json();
  }

  async function api(path, opts = {}) {
    return fetchJSON(`${BASE}${path}`, opts);
  }

  async function tryOffline(paths, parser) {
    for (const p of paths) {
      try {
        const r = await fetch(p, { signal: AbortSignal.timeout(4000) });
        if (!r.ok) continue;
        const j = await r.json();
        return parser ? parser(j) : j;
      } catch (_) { /* next */ }
    }
    return null;
  }

  function renderNav(activeId, containerId = "mesie-nav") {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.className = "mesie-nav";
    el.innerHTML = APPS.map(a =>
      `<a href="${a.href}" class="${a.id === activeId ? "active" : ""}">${a.label}</a>`
    ).join('<span class="sep">·</span>');
  }

  function serviceLink(serviceId) {
    return SERVICE_LINKS[serviceId] || "../platform-hub/";
  }

  return {
    base: BASE,
    apps: APPS,
    serviceLink,
    renderNav,
    models: () => api("/processor/models"),
    platform: () => api("/processor/platform"),
    status: () => api("/processor/status"),
    harness: () => api("/processor/harness"),
    design: () => api("/processor/design"),
    invoke: (serviceId, payload = {}, missionId = "web-mvp") =>
      api(`/processor/platform/${serviceId}/invoke`, {
        method: "POST",
        body: JSON.stringify({ payload, mission_id: missionId }),
      }),
    encode: (text, model = "ST-φ-256") =>
      api("/processor/compute/encode", {
        method: "POST",
        body: JSON.stringify({ payload: text, model }),
      }),
    benchmark: (model = "ST-φ-256", trials = 100) =>
      api("/processor/compute/benchmark", {
        method: "POST",
        body: JSON.stringify({ model, trials }),
      }),
    virtualSilicon: () => api("/processor/virtual-silicon"),
    chips: () => api("/processor/chips"),
    certifyChip: (chipId = "MESIE-VS1") =>
      api("/processor/virtual-chip", {
        method: "POST",
        body: JSON.stringify({ chip_id: chipId }),
      }),
    computeProducts: () => api("/processor/compute/products"),
    computeStatus: () => api("/processor/compute/status"),
    computeSquads: () => api("/processor/compute/squads"),
    runSquad: (squadId = "") =>
      api(`/processor/compute/squads/run${squadId ? `?squad_id=${encodeURIComponent(squadId)}` : ""}`, {
        method: "POST",
      }),
    designOrchestrate: (coreId, brief = {}) =>
      api(`/processor/design/cores/${coreId}/orchestrate`, {
        method: "POST",
        body: JSON.stringify({ brief }),
      }),
    designInvoke: (coreId, paradigmId, brief = {}) =>
      api(`/processor/design/cores/${coreId}/invoke`, {
        method: "POST",
        body: JSON.stringify({ paradigm_id: paradigmId, brief }),
      }),
    realityStatus: () => api("/processor/reality/status"),
    realityInvoke: (coreId, brief = {}, paradigmId = null) =>
      api("/processor/reality/invoke", {
        method: "POST",
        body: JSON.stringify({
          agent_id: "web-reality",
          core_id: coreId,
          brief,
          paradigm_id: paradigmId,
        }),
      }),
    surfaces: () => api("/processor/surfaces"),
    appUrl: (appId) => `http://127.0.0.1:8750/websites/${appId}/index.html`,
    worker: (role, action, payload = {}) =>
      api("/processor/grok/worker", {
        method: "POST",
        body: JSON.stringify({ role, action, payload }),
      }),
    pingUniversal: () => fetchJSON(`${UNI}/health`, { timeout: 3000 }).catch(() => null),
    pingCareer: () => fetchJSON(`${CAREER}/health`, { timeout: 3000 }).catch(() => null),
    offlineProducts: () => tryOffline(
      ["../../deliverables/compute/MESIE_COMPUTE_PRODUCTS.json", "../deliverables/compute/MESIE_COMPUTE_PRODUCTS.json"],
      j => j.products || []
    ),
    offlinePlatform: () => tryOffline(
      ["../../deliverables/platform/PLATFORM_MANIFEST.json", "../deliverables/platform/PLATFORM_MANIFEST.json"],
      j => j
    ),
    offlineAuro: () => tryOffline(
      ["../../deliverables/Auro_Native_Speaking_Manifest.json"],
      j => j
    ),
    hermes: () => api("/processor/hermes"),
    hermesNova: () => api("/processor/hermes/nova-protocol"),
    hermesForge: () => api("/processor/hermes/forge", { method: "POST", body: "{}" }),
    hermesInvoke: (workerId, payload = {}) =>
      api(`/processor/hermes/${workerId}/invoke`, {
        method: "POST",
        body: JSON.stringify({ payload }),
      }),
    offlineHermes: () => tryOffline(
      ["../../deliverables/hermes/HERMES_FLEET_MANIFEST.json"],
      j => ({ hermes: j, nova_protocol: null })
    ),
    marketReady: () => api("/processor/market-ready"),
    marketReadyCycle: () => api("/processor/market-ready/cycle", { method: "POST", body: "{}" }),
  };
})();