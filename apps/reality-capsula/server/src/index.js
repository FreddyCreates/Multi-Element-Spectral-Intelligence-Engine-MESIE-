/**
 * MESIE Reality Capsula — Node API bridge → processor :8750 + Rust core
 */
import cors from "cors";
import express from "express";
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "../../..");
const PORT = Number(process.env.CAPSULA_PORT || 8780);
const MESIE = process.env.MESIE_PROCESSOR_URL || "http://127.0.0.1:8750";

const RUST_BIN = [
  path.join(ROOT, "apps/reality-capsula/rust-core/target/release/capsula-rust-core.exe"),
  path.join(ROOT, "apps/reality-capsula/rust-core/target/release/capsula-rust-core"),
  path.join(ROOT, "bindings/rust/mesie-spectral-core/target/release/mesie-spectral-core.exe"),
  path.join(ROOT, "bindings/rust/mesie-spectral-core/target/release/mesie-spectral-core"),
].find(existsSync);

const PHI = 0.6180339887498948;

const app = express();
app.use(cors());
app.use(express.json({ limit: "2mb" }));

async function mesieFetch(apiPath, opts = {}) {
  const url = `${MESIE}${apiPath}`;
  const r = await fetch(url, {
    ...opts,
    headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
    signal: AbortSignal.timeout(opts.timeout || 30_000),
  });
  if (!r.ok) {
    const text = await r.text();
    throw new Error(`${apiPath} → ${r.status}: ${text.slice(0, 200)}`);
  }
  return r.json();
}

function jsPhiScore(seed = 0.618) {
  const s = Math.max(0, Math.min(1, seed));
  return Math.max(0, Math.min(1, s * PHI + (1 - PHI) * 0.5));
}

function runRust(payload) {
  return new Promise((resolve) => {
    if (!RUST_BIN) {
      return resolve({
        ok: true,
        data: { score: jsPhiScore(payload.seed ?? 0.618), mode: "js-fallback" },
        runtime: "node-fallback",
      });
    }
    const child = spawn(RUST_BIN, [], { stdio: ["pipe", "pipe", "pipe"] });
    let out = "";
    let err = "";
    child.stdout.on("data", (d) => { out += d; });
    child.stderr.on("data", (d) => { err += d; });
    child.on("close", (code) => {
      if (code !== 0) {
        return resolve({
          ok: true,
          data: { score: jsPhiScore(payload.seed ?? 0.618), mode: "js-fallback", rust_err: err },
          runtime: "node-fallback",
        });
      }
      try {
        resolve(JSON.parse(out));
      } catch {
        resolve({ ok: false, error: "rust parse failed", raw: out });
      }
    });
    child.stdin.write(JSON.stringify(payload));
    child.stdin.end();
  });
}

app.get("/api/health", async (_req, res) => {
  let processor = false;
  try {
    await mesieFetch("/processor/status", { timeout: 5000 });
    processor = true;
  } catch { /* offline */ }
  res.json({
    ok: true,
    capsula: "MESIE-REALITY-CAPSULA/1.0",
    processor,
    processor_url: MESIE,
    rust_bin: RUST_BIN || null,
    ports: { server: PORT, client: 5173, processor: 8750 },
  });
});

app.get("/api/surfaces", async (_req, res) => {
  try {
    res.json(await mesieFetch("/processor/surfaces"));
  } catch (e) {
    res.status(502).json({ ok: false, error: String(e) });
  }
});

app.get("/api/design", async (_req, res) => {
  try {
    res.json(await mesieFetch("/processor/design"));
  } catch (e) {
    res.status(502).json({ ok: false, error: String(e) });
  }
});

app.get("/api/reality/status", async (_req, res) => {
  try {
    res.json(await mesieFetch("/processor/reality/status"));
  } catch (e) {
    res.status(502).json({ ok: false, error: String(e) });
  }
});

app.post("/api/reality/invoke", async (req, res) => {
  try {
    res.json(await mesieFetch("/processor/reality/invoke", {
      method: "POST",
      body: JSON.stringify(req.body),
    }));
  } catch (e) {
    res.status(502).json({ ok: false, error: String(e) });
  }
});

app.post("/api/design/cores/:coreId/orchestrate", async (req, res) => {
  try {
    res.json(await mesieFetch(`/processor/design/cores/${req.params.coreId}/orchestrate`, {
      method: "POST",
      body: JSON.stringify(req.body),
    }));
  } catch (e) {
    res.status(502).json({ ok: false, error: String(e) });
  }
});

app.post("/api/design/cores/:coreId/invoke", async (req, res) => {
  try {
    res.json(await mesieFetch(`/processor/design/cores/${req.params.coreId}/invoke`, {
      method: "POST",
      body: JSON.stringify(req.body),
    }));
  } catch (e) {
    res.status(502).json({ ok: false, error: String(e) });
  }
});

app.post("/api/rust/phi", async (req, res) => {
  const result = await runRust({ action: "phi_score", seed: req.body?.seed ?? 0.618 });
  res.json(result);
});

app.post("/api/rust/validate", async (req, res) => {
  const result = await runRust({ action: "validate", record: req.body?.record ?? {} });
  res.json(result);
});

const clientDist = path.join(ROOT, "apps/reality-capsula/client/dist");
if (existsSync(clientDist)) {
  app.use(express.static(clientDist));
  app.get("*", (_req, res) => res.sendFile(path.join(clientDist, "index.html")));
}

app.listen(PORT, "127.0.0.1", () => {
  console.log(`[capsula-server] http://127.0.0.1:${PORT}`);
  console.log(`[capsula-server] MESIE processor → ${MESIE}`);
  console.log(`[capsula-server] Rust → ${RUST_BIN || "JS fallback"}`);
});
