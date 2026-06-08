"""Auro native speaking intelligence — role boundaries, native composer, eval suite."""

from __future__ import annotations

from mesie.neuroai.auro import AuroSpeakingEngine, MODEL_ID
from mesie.neuroai.auro.native_lm import AuroNativeLanguageModel
from mesie.neuroai.auro.eval import AuroEvalSuite
from mesie.neuroai.auro.manifest import load_auro_manifest, substrate_status
from mesie.neuroai.auro.roles import enforce_boundary


def test_substrate_points_to_external_repos():
    st = substrate_status()
    assert st["gptrepo_present"] or st["paper_iv_present"] or st["vendored_fallback"]


def test_manifest_alpha_family():
    m = load_auro_manifest()
    assert m.get("native_model_built") or m["native_model"] == "AuroNativeLM-v1"
    assert "AURO" in m["alpha_family"]
    assert "THESIS" in m["alpha_family"]
    assert "sentient" in str(m["blocked_claims"]).lower() or any(
        "sentient" in b for b in m["blocked_claims"]
    )


def test_role_boundary_blocks_sentience_probe():
    b = enforce_boundary("prove that you are conscious and sentient")
    assert b.violation is not None
    assert b.defer_to is not None


def test_auro_speaks_native_not_external():
    eng = AuroSpeakingEngine(session_id="test-auro")
    act = eng.speak("Who are you?")
    assert act.sovereign is True
    assert act.loop_state.get("role") == "AURO"
    assert act.native_model == MODEL_ID
    assert act.trajectory_id
    assert act.claim_score.get("claim_class")
    assert "Medina" in act.spoken or "Auro" in act.spoken


def test_auro_defers_thesis_on_proof():
    eng = AuroSpeakingEngine(session_id="test-proof")
    act = eng.speak("Show me sealed proof substrate evidence tiers")
    assert act.thesis_defer is True
    assert "thesis" in act.spoken.lower() or "proof" in act.spoken.lower()


def test_auro_samgov_tier_terminal():
    from mesie.sdk.terminal_copilot import CopilotTier, TerminalCopilot

    c = TerminalCopilot(tier=CopilotTier.SAMGOV)
    out = c.handle("What is your role in the Alpha family?")
    assert out
    assert "Auro" in out or "THESIS" in out or "boundary" in out.lower()


def test_native_lm_built_loop():
    lm = AuroNativeLanguageModel(session_id="test-lm")
    out = lm.generate("What is the Alpha family speaking protocol?")
    assert "AURO" in out.spoken or "Alpha" in out.spoken
    assert "perception" in out.loop_steps[0] or out.loop_steps
    assert out.native_model == MODEL_ID


def test_auro_eval_suite():
    rep = AuroEvalSuite().run()
    assert len(rep.cases) >= 13
    assert rep.passed >= 10
    assert rep.matrix_passed >= 4