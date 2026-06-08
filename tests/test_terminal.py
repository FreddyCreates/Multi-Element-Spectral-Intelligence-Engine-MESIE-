"""SDK terminal layer — PowerShell-first."""

from __future__ import annotations

import sys

from mesie.sdk.terminal import ShellKind, default_session, detect_shell, open_surfaces, tool_commands_for_catalog


def test_detect_shell_windows_powershell():
    prof = detect_shell()
    if sys.platform == "win32":
        assert prof.kind in (ShellKind.POWERSHELL, ShellKind.PWSH, ShellKind.CMD)


def test_format_chain_powershell():
    session = default_session()
    if session.profile.kind in (ShellKind.POWERSHELL, ShellKind.PWSH, ShellKind.CMD):
        chained = session.format_command("python a.py && python b.py")
        assert " && " not in chained
        assert "python a.py" in chained
        assert "python b.py" in chained


def test_catalog_dual_commands():
    cmds = tool_commands_for_catalog("python scripts/run_is_this_true.py")
    assert "powershell_command" in cmds
    assert "bash_command" in cmds


def test_open_surfaces_includes_sdk_and_ps1():
    names = {s["surface"] for s in open_surfaces()}
    assert "MAESIClient.terminal" in names
    assert "scripts/MESIE.ps1" in names


def test_maesi_client_terminal():
    from mesie.sdk import MAESIClient

    client = MAESIClient()
    st = client.terminal.status()
    assert "profile" in st
    assert client.terminal.profile.kind in ShellKind