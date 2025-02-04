"""GitHub Actions integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Set, cast

from tox.execute.request import StdinSource
from tox.tox_env.python.runner import add_extras_to_env, add_skip_missing_interpreters_to_core
from tox.tox_env.runner import RunToxEnv

from ._installer import ReadOnlyUvInstaller
from ._venv import UvVenv

if TYPE_CHECKING:
    from tox.tox_env.package import Package


class UvVenvLockRunner(UvVenv, RunToxEnv):
    InstallerClass = ReadOnlyUvInstaller

    @staticmethod
    def id() -> str:
        return "uv-venv-lock-runner"

    def _register_package_conf(self) -> bool:  # noqa: PLR6301
        return False

    @property
    def _package_tox_env_type(self) -> str:
        raise NotImplementedError

    @property
    def _external_pkg_tox_env_type(self) -> str:
        raise NotImplementedError

    def _build_packages(self) -> list[Package]:
        raise NotImplementedError

    def register_config(self) -> None:
        super().register_config()
        add_extras_to_env(self.conf)
        add_skip_missing_interpreters_to_core(self.core, self.options)

    def _setup_env(self) -> None:
        super()._setup_env()
        cmd = ["uv", "sync", "--frozen"]
        for extra in cast(Set[str], sorted(self.conf["extras"])):
            cmd.extend(("--extra", extra))
        outcome = self.execute(cmd, stdin=StdinSource.OFF, run_id="uv-sync", show=False)
        outcome.assert_success()

    @property
    def environment_variables(self) -> dict[str, str]:
        env = super().environment_variables
        env["UV_PROJECT_ENVIRONMENT"] = str(self.venv_dir)
        return env


__all__ = [
    "UvVenvLockRunner",
]
