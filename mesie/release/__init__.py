"""Release packaging — bootstrap, install hooks, release readiness."""

from mesie.release.bootstrap import ensure_bootstrapped, bootstrap
from mesie.release.paths import resolve_workspace_root, user_config_dir

__all__ = ["ensure_bootstrapped", "bootstrap", "user_config_dir", "resolve_workspace_root"]