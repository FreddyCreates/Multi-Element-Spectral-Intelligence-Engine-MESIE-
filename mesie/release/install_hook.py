"""Post-install hook — embed terminal + copilot on pip install."""

from __future__ import annotations

import sys

try:
    from setuptools.command.develop import develop
    from setuptools.command.install import install
except ImportError:
    MesieInstall = None
    MesieDevelop = None
else:

    def _run_bootstrap() -> None:
        try:
            from mesie.release.bootstrap import bootstrap

            install_profile = sys.platform == "win32"
            bootstrap(install_profile=install_profile, quiet=False)
            print("MESIE: run 'maesi' for terminal + AI copilot (sovereign | samgov | research)")
        except Exception as exc:
            print(f"MESIE bootstrap deferred — run 'mesie-bootstrap --install-profile': {exc}")

    class MesieInstall(install):
        def run(self) -> None:
            install.run(self)
            _run_bootstrap()

    class MesieDevelop(develop):
        def run(self) -> None:
            develop.run(self)
            _run_bootstrap()