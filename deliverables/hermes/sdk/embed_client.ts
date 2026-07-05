/** @itsnotailabs/hermes-embed — ST-φ edge embed client */
export async function hermesEmbed(text: string, model = "ST-φ-256", base = "https://hermes-embed.workers.dev") {
  const r = await fetch(`${base}/hermes/embed`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ payload: text, model }),
  });
  return r.json();
}
