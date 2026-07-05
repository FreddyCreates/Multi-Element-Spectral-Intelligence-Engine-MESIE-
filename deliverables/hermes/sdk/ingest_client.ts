/** @itsnotailabs/hermes-ingest — NOVA PROTOCOL clean ingest */
export async function hermesIngest(record: object, base = "https://hermes-ingest.workers.dev") {
  const r = await fetch(`${base}/hermes/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ record, provenance_hash: crypto.randomUUID() }),
  });
  return r.json();
}
