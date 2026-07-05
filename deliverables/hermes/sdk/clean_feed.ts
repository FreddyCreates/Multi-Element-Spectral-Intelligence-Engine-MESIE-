/** @itsnotailabs/hermes-clean — NOVA clean internet feed filter */
export function cleanFeedRules() {
  return {
    block_unverified_claims: true,
    require_provenance_hash: true,
    spectral_validate: true,
    third_party_inference: false,
  };
}
