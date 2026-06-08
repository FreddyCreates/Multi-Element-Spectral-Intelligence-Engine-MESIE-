"""Install bootstrap — embed terminal + copilot on pip install / first run."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from mesie.release.paths import resolve_workspace_root, script_source, user_config_dir
from mesie.neuroai.auro.substrate_loader import gptrepo_root, neuroai_packet_root

ROOT = resolve_workspace_root()


def bootstrap(*, install_profile: bool = False, quiet: bool = False) -> Dict[str, Any]:
    """Write user config, copy PowerShell module, optional PS profile hook."""
    cfg_dir = user_config_dir()
    cfg_dir.mkdir(parents=True, exist_ok=True)

    for name in ("MESIE.ps1", "Enter-MESIEShell.ps1"):
        src = script_source(name)
        if src and src.is_file():
            shutil.copy2(src, cfg_dir / name)
    dst_ps1 = cfg_dir / "MESIE.ps1"

    import mesie
    from mesie.sdk import __sdk_version__
    from mesie.sdk.terminal import detect_shell
    from mesie.version_info import MESIE_VERSION, MAESI_SDK_VERSION, TERMINAL_SDK_VERSION

    config = {
        "bootstrapped": True,
        "mesie_version": mesie.__version__,
        "sdk_version": __sdk_version__,
        "terminal_sdk_version": TERMINAL_SDK_VERSION,
        "workspace_root": str(ROOT),
        "install_mode": "dev" if (ROOT / "pyproject.toml").is_file() else "pip",
        "config_dir": str(cfg_dir),
        "powershell_module": str(dst_ps1),
        "default_tier": "sovereign",
        "copilot_tiers": ["sovereign", "samgov", "research"],
        "auro_substrate": {
            "gptrepo_root": str(gptrepo_root()),
            "neuroai_packet_root": str(neuroai_packet_root()),
            "native_model": "AuroNativeLM-v1",
        },
        "terminal_profile": detect_shell().to_dict(),
        "entry_commands": {
            "maesi": "maesi",
            "mesie_terminal": "mesie terminal",
            "mesie_tools_shell": "mesie-tools shell",
            "powershell": f". '{dst_ps1}'",
        },
    }
    config_path = cfg_dir / "config.json"
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    profile_snippet = cfg_dir / "MESIE.profile.ps1"
    profile_snippet.write_text(
        "\n".join([
            "# MESIE SDK — auto-loaded terminal helpers",
            f"$MesieConfigDir = '{cfg_dir}'",
            f"$MesieRepoRoot = '{ROOT}'",
            f"if (Test-Path '{dst_ps1}') {{ . '{dst_ps1}' }}",
            "function global:maesi { python -m mesie.release.maesi_entry @args }",
        ]),
        encoding="utf-8",
    )

    profile_installed = False
    if install_profile and sys.platform == "win32":
        docs = Path.home() / "Documents"
        ps_profile = docs / "PowerShell" / "Microsoft.PowerShell_profile.ps1"
        ps_profile.parent.mkdir(parents=True, exist_ok=True)
        hook = f". '{profile_snippet}'"
        existing = ps_profile.read_text(encoding="utf-8") if ps_profile.is_file() else ""
        if hook not in existing:
            ps_profile.write_text(existing + f"\n# MESIE SDK\n{hook}\n", encoding="utf-8")
            profile_installed = True

    result = {**config, "profile_snippet": str(profile_snippet), "profile_installed": profile_installed}
    if not quiet:
        print(f"MESIE bootstrap OK — config: {config_path}")
        if profile_installed:
            print(f"PowerShell profile updated: {ps_profile}")
    return result


def ensure_bootstrapped(*, quiet: bool = True) -> Dict[str, Any]:
    cfg = user_config_dir() / "config.json"
    if cfg.is_file():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
            if data.get("bootstrapped"):
                return data
        except json.JSONDecodeError:
            pass
    return bootstrap(quiet=quiet)


def main(argv: Optional[list[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="mesie-bootstrap")
    parser.add_argument("--install-profile", action="store_true", help="Hook PowerShell profile")
    args = parser.parse_args(argv)
    bootstrap(install_profile=args.install_profile)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())