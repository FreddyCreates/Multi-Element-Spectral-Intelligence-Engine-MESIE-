import { useCallback, useEffect, useState } from "react";
import { api, type DesignCore } from "./api";
import { RealityViewport } from "./RealityViewport";

const STATIC_APPS = [
  { id: "processor", label: "Processor :8750", href: "http://127.0.0.1:8750/websites/platform-hub/index.html" },
  { id: "legacy-reality", label: "Legacy Reality HTML", href: "http://127.0.0.1:8750/websites/reality-engine/index.html" },
];

export default function App() {
  const [cores, setCores] = useState<DesignCore[]>([]);
  const [selectedCore, setSelectedCore] = useState("core_realitas");
  const [selectedParadigm, setSelectedParadigm] = useState("unreal_class");
  const [processor, setProcessor] = useState(false);
  const [rustBin, setRustBin] = useState<string | null>(null);
  const [phiScore, setPhiScore] = useState(0.618);
  const [paradigmCount, setParadigmCount] = useState(200);
  const [protoCount, setProtoCount] = useState(40);
  const [log, setLog] = useState("Ready — React + Node + Rust Capsula");
  const [apps, setApps] = useState<Array<{ id: string; title: string; path: string }>>([]);

  const core = cores.find((c) => c.core_id === selectedCore);

  const load = useCallback(async () => {
    try {
      const [h, d] = await Promise.all([api.health(), api.design()]);
      setProcessor(h.processor);
      setRustBin(h.rust_bin);
      setCores(d.cores || []);
      setParadigmCount(d.paradigm_count || 200);
      setProtoCount(d.canonical_protocol_count || 40);
    } catch (e) {
      setLog(String(e));
    }
    try {
      const s = await api.surfaces();
      setApps(s.apps || []);
    } catch { /* optional */ }
    try {
      const phi = await api.rustPhi(0.618);
      const score = (phi as { data?: { score?: number } }).data?.score;
      if (typeof score === "number") setPhiScore(score);
    } catch { /* fallback */ }
  }, []);

  useEffect(() => { load(); }, [load]);

  const orchestrate = async () => {
    setLog("orchestrating…");
    try {
      const j = await api.orchestrate(selectedCore, { showcase: "capsula", paradigm: selectedParadigm });
      setLog(JSON.stringify(j, null, 2));
    } catch (e) { setLog(String(e)); }
  };

  const realityInvoke = async () => {
    setLog("reality invoke…");
    try {
      const j = await api.realityInvoke({
        agent_id: "capsula-react",
        core_id: selectedCore,
        brief: { showcase: "product" },
        paradigm_id: selectedParadigm,
      });
      setLog(JSON.stringify(j, null, 2));
    } catch (e) { setLog(String(e)); }
  };

  const invokeAgent = async () => {
    setLog("agent invoke…");
    try {
      const j = await api.invokeAgent(selectedCore, selectedParadigm, { brief: "capsula" });
      setLog(JSON.stringify(j, null, 2));
    } catch (e) { setLog(String(e)); }
  };

  return (
    <>
      <nav className="nav">
        <strong style={{ marginRight: "0.5rem", fontSize: "0.85rem" }}>MESIE Capsula</strong>
        <a href="/" className="active">Reality</a>
        {STATIC_APPS.map((a) => (
          <a key={a.id} href={a.href} target="_blank" rel="noreferrer">{a.label}</a>
        ))}
        {apps.slice(0, 6).map((a) => (
          <a key={a.id} href={a.path} target="_blank" rel="noreferrer">{a.title}</a>
        ))}
      </nav>

      <section className="metrics">
        <div className="metric-card"><div className="metric-label">Processor</div><div className="metric-value" style={{ color: processor ? "var(--ok)" : "var(--muted)" }}>{processor ? "LIVE" : "OFF"}</div></div>
        <div className="metric-card"><div className="metric-label">Agents</div><div className="metric-value">{paradigmCount}</div></div>
        <div className="metric-card"><div className="metric-label">Protocols</div><div className="metric-value">{protoCount}+</div></div>
        <div className="metric-card"><div className="metric-label">Rust φ</div><div className="metric-value">{phiScore.toFixed(3)}</div></div>
      </section>

      <div className="layout">
        <aside className="panel">
          <h2 className="muted" style={{ fontSize: "0.7rem", textTransform: "uppercase", marginBottom: "0.5rem" }}>Reality Cores</h2>
          {cores.map((c) => (
            <button
              key={c.core_id}
              type="button"
              className={`core-btn ${c.core_id === selectedCore ? "active" : ""}`}
              onClick={() => {
                setSelectedCore(c.core_id);
                const p = c.paradigms?.[0]?.paradigm_id;
                if (p) setSelectedParadigm(p);
              }}
            >
              <strong>{c.latin_name}</strong>
              <div className="muted">{c.paradigm_count} agents · {c.reality_class}</div>
            </button>
          ))}
          <p className="muted" style={{ fontSize: "0.65rem", marginTop: "0.75rem" }}>
            Rust: {rustBin ? "native" : "JS fallback"}
          </p>
        </aside>

        <main>
          <div style={{ padding: "0.75rem 1rem" }}>
            <h1 style={{ fontSize: "1.2rem" }}>{core?.latin_name || "Core Realitas"}</h1>
            <p className="muted">{core?.english_title} · Unreal-class React showcase</p>
          </div>
          <RealityViewport coreId={selectedCore} phiScore={phiScore} />
        </main>

        <aside className="panel panel-right">
          <h2 className="muted" style={{ fontSize: "0.7rem", textTransform: "uppercase" }}>Agents ({core?.paradigms?.length || 20})</h2>
          <div style={{ maxHeight: 220, overflowY: "auto" }}>
            {(core?.paradigms || []).map((p) => (
              <div
                key={p.paradigm_id}
                className={`agent-row ${p.paradigm_id === selectedParadigm ? "selected" : ""}`}
                onClick={() => setSelectedParadigm(p.paradigm_id)}
              >
                <strong>{p.name}</strong>
                <div className="muted">{p.latin_agent} · {p.stack}</div>
              </div>
            ))}
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginTop: "0.75rem" }}>
            <button type="button" className="btn-primary" onClick={orchestrate}>Orchestrate</button>
            <button type="button" className="btn-ghost" onClick={realityInvoke}>Reality</button>
            <button type="button" className="btn-ghost" onClick={invokeAgent}>Agent</button>
          </div>
          <pre className="log">{log}</pre>
        </aside>
      </div>
    </>
  );
}
