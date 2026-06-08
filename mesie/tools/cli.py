"""Unified CLI for native MESIE / MAESI / NeuroAIX tools."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from mesie.sdk.terminal import default_session, open_surfaces, open_terminal, tool_commands_for_catalog
from mesie.tools.registry import SKILL_CATEGORIES, TOOLS, tool_by_id


from mesie.release.paths import resolve_workspace_root

ROOT = resolve_workspace_root()


def _run_command(cmd: str) -> int:
    session = default_session(ROOT)
    print(f"$ {session.format_command(cmd)}")
    if cmd.startswith("type ") and sys.platform != "win32":
        p = Path(cmd.split(maxsplit=1)[1])
        print(p.read_text(encoding="utf-8")[:2000])
        return 0
    return session.run(cmd).returncode


def cmd_list(_: argparse.Namespace) -> int:
    session = default_session(ROOT)
    print("MESIE / MAESI / NeuroAIX Native Tools\n")
    print(f"Terminal: {session.profile.kind.value} ({session.profile.executable})\n")
    for cat, title in SKILL_CATEGORIES.items():
        print(f"## {title}")
        for t in TOOLS:
            if t.category == cat:
                print(f"  {t.id:20}  {t.name}")
        print()
    print(f"Total: {len(TOOLS)} tools | Skills: {len({t.skill_name for t in TOOLS})}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    t = tool_by_id(args.tool)
    if not t:
        print(f"Unknown tool: {args.tool}", file=sys.stderr)
        return 1
    cmd = t.command
    if args.extra:
        cmd = f"{cmd} {args.extra}"
    return _run_command(cmd)


def cmd_shell(args: argparse.Namespace) -> int:
    from mesie.sdk.terminal_copilot import run_copilot_terminal

    tier = getattr(args, "tier", "sovereign") or "sovereign"
    return run_copilot_terminal(tier=tier)


def cmd_open_terminal(args: argparse.Namespace) -> int:
    pid = open_terminal(command=args.command or None, cwd=ROOT)
    print(f"Opened terminal (pid={pid})")
    return 0 if pid else 1


def cmd_surfaces(_: argparse.Namespace) -> int:
    print(json.dumps(open_surfaces(), indent=2))
    return 0


def cmd_skills(_: argparse.Namespace) -> int:
    from mesie.tools.generate_skills import generate_all

    n = generate_all()
    print(f"Generated {n} skills under .grok/skills/")
    return 0


def cmd_catalog(args: argparse.Namespace) -> int:
    session = default_session(ROOT)
    by_skill: dict[str, list[dict]] = {}
    for t in TOOLS:
        cmds = tool_commands_for_catalog(t.command)
        by_skill.setdefault(t.skill_name, []).append(
            {
                "id": t.id,
                "name": t.name,
                "category": t.category,
                "command": t.command,
                "powershell_command": cmds["powershell_command"],
                "bash_command": cmds["bash_command"],
                "deliverable": t.deliverable,
                "triggers": t.triggers,
            }
        )
    import mesie
    from mesie.sdk import __sdk_version__

    payload = {
        "suite": "MESIE / MAESI / NeuroAIX",
        "mesie_version": mesie.__version__,
        "sdk_version": __sdk_version__,
        "terminal_profile": session.profile.to_dict(),
        "terminal_surfaces": open_surfaces(),
        "tool_count": len(TOOLS),
        "skill_count": len(by_skill) + 1,
        "categories": SKILL_CATEGORIES,
        "skills": {k: v for k, v in sorted(by_skill.items())},
    }
    out = ROOT / "deliverables" / "MESIE_Native_Tools_Catalog.json"
    if args.output:
        out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out} ({len(TOOLS)} tools, {len(by_skill)} skills + hub)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mesie-tools",
        description="Native MESIE / MAESI / NeuroAIX tool suite (PowerShell-first on Windows)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List all native tools")
    p_list.set_defaults(func=cmd_list)

    p_run = sub.add_parser("run", help="Run a native tool by id")
    p_run.add_argument("tool", help="Tool id (e.g. monte-carlo, maesi, octopus)")
    p_run.add_argument("extra", nargs="?", default="", help="Extra args appended to command")
    p_run.set_defaults(func=cmd_run)

    p_shell = sub.add_parser("shell", help="Interactive MESIE terminal + AI copilot")
    p_shell.add_argument("--tier", choices=["sovereign", "samgov", "research"], default="sovereign")
    p_shell.set_defaults(func=cmd_shell)

    p_open = sub.add_parser("open-terminal", help="Open OS terminal at repo root")
    p_open.add_argument("--command", default="", help="Optional command to run in new terminal")
    p_open.set_defaults(func=cmd_open_terminal)

    p_surf = sub.add_parser("surfaces", help="List where SDK can open full terminals")
    p_surf.set_defaults(func=cmd_surfaces)

    p_sk = sub.add_parser("skills", help="Regenerate .grok/skills from registry")
    p_sk.set_defaults(func=cmd_skills)

    p_cat = sub.add_parser("catalog", help="Export native tools catalog JSON")
    p_cat.add_argument("-o", "--output", default="", help="Output path (default: deliverables/)")
    p_cat.set_defaults(func=cmd_catalog)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())