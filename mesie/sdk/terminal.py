"""SDK terminal layer — PowerShell-first on Windows, bash elsewhere.

Edge contested deploys often land on issued Windows laptops. The SDK treats
PowerShell as a full terminal peer, not a fallback after bash examples.
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

from mesie.release.paths import resolve_workspace_root

ROOT = resolve_workspace_root()


class ShellKind(str, Enum):
    POWERSHELL = "powershell"
    PWSH = "pwsh"
    CMD = "cmd"
    BASH = "bash"
    SH = "sh"


CHAIN_OPS = {
    ShellKind.POWERSHELL: "; ",
    ShellKind.PWSH: "; ",
    ShellKind.CMD: " & ",
    ShellKind.BASH: " && ",
    ShellKind.SH: " && ",
}


@dataclass
class TerminalProfile:
    kind: ShellKind
    executable: str
    args_prefix: List[str]
    is_windows: bool
    supports_chain: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind.value,
            "executable": self.executable,
            "args_prefix": self.args_prefix,
            "is_windows": self.is_windows,
            "chain_operator": self.supports_chain.strip(),
        }


@dataclass
class TerminalSession:
    """MAESI SDK terminal — run tools, chain scripts, open interactive shells."""

    profile: TerminalProfile
    cwd: Path = field(default_factory=lambda: ROOT)
    history: List[str] = field(default_factory=list)

    def format_chain(self, *commands: str) -> str:
        op = self.profile.supports_chain
        parts = [c.strip() for c in commands if c.strip()]
        return op.join(parts)

    def format_command(self, command: str) -> str:
        """Normalize && / ; chains for the active shell."""
        if " && " in command and self.profile.kind in (ShellKind.POWERSHELL, ShellKind.PWSH, ShellKind.CMD):
            return self.format_chain(*command.split(" && "))
        return command.strip()

    def run(self, command: str, *, capture: bool = False, timeout: Optional[float] = None) -> subprocess.CompletedProcess[str]:
        cmd = self.format_command(command)
        self.history.append(cmd)
        if capture:
            return subprocess.run(
                cmd,
                shell=True,
                cwd=str(self.cwd),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        return subprocess.run(cmd, shell=True, cwd=str(self.cwd), timeout=timeout)

    def run_tool(self, tool_id: str, extra: str = "") -> int:
        from mesie.tools.registry import tool_by_id

        t = tool_by_id(tool_id)
        if not t:
            raise ValueError(f"Unknown tool: {tool_id}")
        args = [sys.executable, "-m", "mesie.tools.cli", "run", tool_id]
        if extra:
            args.append(extra)
        return subprocess.run(args, cwd=str(self.cwd)).returncode

    def open_interactive(self, *, command: Optional[str] = None) -> Optional[int]:
        """Open a new terminal window at cwd (PowerShell on Windows)."""
        return open_terminal(command=command, cwd=self.cwd, profile=self.profile)

    def script_path(self, name: str = "MESIE.ps1") -> Path:
        return self.cwd / "scripts" / name

    def status(self) -> Dict[str, Any]:
        return {
            "profile": self.profile.to_dict(),
            "cwd": str(self.cwd),
            "platform": sys.platform,
            "history_len": len(self.history),
            "sdk_entry_ps1": str(self.script_path()),
            "cli": "python -m mesie.tools.cli",
        }


def _which(name: str) -> Optional[str]:
    return shutil.which(name)


def detect_shell(prefer: Optional[ShellKind] = None) -> TerminalProfile:
    """Detect best shell — PowerShell/pwsh preferred on Windows."""
    if prefer:
        return _profile_for(prefer)

    if sys.platform == "win32":
        if _which("pwsh"):
            return _profile_for(ShellKind.PWSH)
        ps = _which("powershell") or r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
        if Path(ps).exists():
            return _profile_for(ShellKind.POWERSHELL)
        return _profile_for(ShellKind.CMD)

    if _which("bash"):
        return _profile_for(ShellKind.BASH)
    return _profile_for(ShellKind.SH)


def _profile_for(kind: ShellKind) -> TerminalProfile:
    if kind == ShellKind.PWSH:
        exe = _which("pwsh") or "pwsh"
        return TerminalProfile(kind, exe, [], sys.platform == "win32", CHAIN_OPS[kind])
    if kind == ShellKind.POWERSHELL:
        exe = _which("powershell") or r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
        return TerminalProfile(kind, exe, [], True, CHAIN_OPS[kind])
    if kind == ShellKind.CMD:
        exe = _which("cmd") or "cmd.exe"
        return TerminalProfile(kind, exe, ["/c"], True, CHAIN_OPS[kind])
    if kind == ShellKind.BASH:
        exe = _which("bash") or "bash"
        return TerminalProfile(kind, exe, ["-lc"], False, CHAIN_OPS[kind])
    exe = _which("sh") or "sh"
    return TerminalProfile(kind, exe, ["-c"], False, CHAIN_OPS[kind])


def default_session(cwd: Optional[Union[str, Path]] = None) -> TerminalSession:
    return TerminalSession(profile=detect_shell(), cwd=Path(cwd) if cwd else ROOT)


def _quote_path(path: str) -> str:
    if sys.platform == "win32":
        return "'" + path.replace("'", "''") + "'"
    return shlex.quote(path)


def open_terminal(
    *,
    command: Optional[str] = None,
    cwd: Optional[Union[str, Path]] = None,
    profile: Optional[TerminalProfile] = None,
) -> Optional[int]:
    """Spawn interactive terminal — PowerShell window on Windows, bash elsewhere."""
    prof = profile or detect_shell()
    work = Path(cwd) if cwd else ROOT
    work_str = str(work.resolve())

    if prof.kind in (ShellKind.POWERSHELL, ShellKind.PWSH):
        inner = f"Set-Location -LiteralPath {_quote_path(work_str)}"
        if command:
            session = TerminalSession(prof, work)
            inner += f"; {session.format_command(command)}"
        args = [
            prof.executable,
            "-NoExit",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            inner,
        ]
        if _which("wt.exe") and command is None:
            args = ["wt.exe", prof.executable, "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", inner]
        proc = subprocess.Popen(args, cwd=work_str)
        return proc.pid

    if prof.kind == ShellKind.CMD:
        inner = f'cd /d "{work_str}"'
        if command:
            session = TerminalSession(prof, work)
            inner += f" & {session.format_command(command)}"
        proc = subprocess.Popen(["cmd.exe", "/k", inner], cwd=work_str)
        return proc.pid

    inner = f"cd {shlex.quote(work_str)}"
    if command:
        session = TerminalSession(prof, work)
        inner += f" && {session.format_command(command)}"
    proc = subprocess.Popen([prof.executable, "-lc", inner], cwd=work_str)
    return proc.pid


def tool_commands_for_catalog(command: str) -> Dict[str, str]:
    """Export bash + PowerShell variants for registry catalog."""
    session_ps = TerminalSession(_profile_for(ShellKind.POWERSHELL), ROOT)
    session_bash = TerminalSession(_profile_for(ShellKind.BASH), ROOT)
    return {
        "command": command,
        "powershell_command": session_ps.format_command(command),
        "bash_command": session_bash.format_command(command),
    }


def open_surfaces() -> List[Dict[str, str]]:
    """Where the SDK can open a full terminal session."""
    return [
        {
            "surface": "MAESIClient.terminal",
            "usage": "client.terminal.open_interactive()",
            "notes": "SDK property — opens PowerShell on Windows from Python",
        },
        {
            "surface": "mesie-tools shell",
            "usage": "python -m mesie.tools.cli shell",
            "notes": "Interactive REPL-style shell with tool runner",
        },
        {
            "surface": "mesie-tools open-terminal",
            "usage": "python -m mesie.tools.cli open-terminal [--command CMD]",
            "notes": "Spawn new OS terminal window at repo root",
        },
        {
            "surface": "scripts/MESIE.ps1",
            "usage": ". .\\scripts\\MESIE.ps1; Invoke-MESIETool readiness",
            "notes": "PowerShell module — primary edge entry on Windows",
        },
        {
            "surface": "scripts/Enter-MESIEShell.ps1",
            "usage": ".\\scripts\\Enter-MESIEShell.ps1",
            "notes": "Opens Windows Terminal / PowerShell preloaded with SDK helpers",
        },
        {
            "surface": "deliverables/neuroswarmai_com/reproduce.ps1",
            "usage": ".\\deliverables\\neuroswarmai_com\\reproduce.ps1",
            "notes": "Customer / GSA contractor repro harness",
        },
        {
            "surface": "VS Code / Cursor integrated terminal",
            "usage": "Default profile: PowerShell; run scripts/MESIE.ps1 dot-source",
            "notes": "IDE terminal is a first-class peer — same commands",
        },
        {
            "surface": "Windows Terminal profile",
            "usage": "wt -p PowerShell -d <repo> python -m mesie.tools.cli list",
            "notes": "Ship MESIE.ps1 path in appliance manifest for WT bookmarks",
        },
        {
            "surface": "Trust remediation agents",
            "usage": "mesie/agents/trust_remediation.py via terminal.run()",
            "notes": "Agent commits use shell-aware subprocess",
        },
        {
            "surface": "Enterprise copilot run_tool",
            "usage": "copilot invokes mesie-tools run <id> through terminal layer",
            "notes": "Sovereign copilot tool execution on edge appliance",
        },
    ]