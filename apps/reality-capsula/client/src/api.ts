const API = "/api";

async function fetchJSON<T>(path: string, opts?: RequestInit): Promise<T> {
  const r = await fetch(`${API}${path}`, {
    ...opts,
    headers: { "Content-Type": "application/json", ...(opts?.headers || {}) },
  });
  if (!r.ok) throw new Error(`${path} → ${r.status}`);
  return r.json();
}

export type DesignCore = {
  core_id: string;
  latin_name: string;
  english_title: string;
  reality_class: string;
  paradigm_count: number;
  paradigms: Array<{
    paradigm_id: string;
    name: string;
    stack: string;
    latin_agent: string;
    role: string;
    language?: string;
  }>;
};

export const api = {
  health: () => fetchJSON<{ processor: boolean; rust_bin: string | null }>("/health"),
  design: () => fetchJSON<{ cores: DesignCore[]; paradigm_count: number; canonical_protocol_count?: number }>("/design"),
  surfaces: () => fetchJSON<{ apps: Array<{ id: string; title: string; path: string }> }>("/surfaces"),
  realityStatus: () => fetchJSON<Record<string, unknown>>("/reality/status"),
  orchestrate: (coreId: string, brief: Record<string, unknown>) =>
    fetchJSON(`/design/cores/${coreId}/orchestrate`, {
      method: "POST",
      body: JSON.stringify({ brief }),
    }),
  invokeAgent: (coreId: string, paradigmId: string, brief: Record<string, unknown> = {}) =>
    fetchJSON(`/design/cores/${coreId}/invoke`, {
      method: "POST",
      body: JSON.stringify({ paradigm_id: paradigmId, brief }),
    }),
  realityInvoke: (body: Record<string, unknown>) =>
    fetchJSON("/reality/invoke", { method: "POST", body: JSON.stringify(body) }),
  rustPhi: (seed = 0.618) =>
    fetchJSON("/rust/phi", { method: "POST", body: JSON.stringify({ seed }) }),
};
