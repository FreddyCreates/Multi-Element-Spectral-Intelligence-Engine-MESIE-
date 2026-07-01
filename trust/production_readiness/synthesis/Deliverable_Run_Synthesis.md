# Deliverable Run Synthesis

Generated: 2026-06-25T20:26:33Z

Both snapshots are preserved under each suite's `runs/` folder. Canonical paths were restored to the **committed full** versions from git.

## sov_del (sovereign_local)

### `NativeAI_sov_del.json`
- Committed: `deliverables\native_ai\sovereign_local\runs\20260625T202633Z_committed_full_sov_del\NativeAI_sov_del.json`
- Partial (June 24 disk): `deliverables\native_ai\sovereign_local\runs\20260625T202633Z_partial_local_sov_del\NativeAI_sov_del.json`
- `composition`: object — {"json_chars_a": 2410, "json_chars_b": 2404, "delta_chars": -6}
- `conclusion`: scalar — {"a": "reasoning: moderate signal \u2014 monitor via mini heart | emergence=0.1404", "b": "reasoning: moderate signal \u2014 monitor via mini heart | emergence=0.0611"}
- `elapsed_ms`: scalar — {"a": 411.87, "b": 645.68}
- `formal_models`: object — {"json_chars_a": 854, "json_chars_b": 858, "delta_chars": 4}
- `generated_at`: scalar — {"a": "2026-06-07T18:02:39Z", "b": "2026-06-24T19:19:58Z"}
- `minted_token`: object — {"json_chars_a": 172, "json_chars_b": 172, "delta_chars": 0}
- `plain_summary`: scalar — {"a": "Native AI [SOLUS]: sov_del \u2014 Logic \u2297 Reasoning \u2297 Emergence \u2297 Adaptation. Neighbors=2, token=f8467161f7cb\u2026, vault=232, work=214.7248, 411.9ms local.", "b": "Native AI [S
- `query`: object — {"json_chars_a": 393, "json_chars_b": 389, "delta_chars": -4}

### `NativeAI_sov_del_vault.json`
- Committed: `deliverables\native_ai\sovereign_local\runs\20260625T202633Z_committed_full_sov_del\NativeAI_sov_del_vault.json`
- Partial (June 24 disk): `deliverables\native_ai\sovereign_local\runs\20260625T202633Z_partial_local_sov_del\NativeAI_sov_del_vault.json`
- `last_entry`: object — {"json_chars_a": 21185, "json_chars_b": 11894, "delta_chars": -9291}
- `total_work_units`: scalar — {"a": 214.7248, "b": 949.9038}
- `vault_size`: scalar — {"a": 232, "b": 535}

## theater_alpha_week_001 (mission_world)

### `theater_alpha_week_001_state.json`
- Committed: `library\mission_worlds\runs\20260625T202633Z_committed_full_theater_alpha_week_001\theater_alpha_week_001_state.json`
- Partial (June 24 disk): `library\mission_worlds\runs\20260625T202633Z_partial_local_theater_alpha_week_001\theater_alpha_week_001_state.json`
- **Ticks:** committed 56 → partial had 8 (lost 48)
- **Ops only in full run:** op_day2_ew_probe, op_day3_strike_window, op_day4_jam_escalation, op_day5_attrition_reform, op_day6_10k_surge, op_day7_sustainment
- **Peak agents:** {'old': 10000, 'new': 500}
- **Attrition:** {'old': 0.564, 'new': 0.023999999999999997}
- Partial rerun kept only early-day ISR baseline ticks; full week ops (days 2–7, 10K surge) are present in the committed snapshot only.

