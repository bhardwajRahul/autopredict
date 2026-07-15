"""Import every module shipped by an installed distribution.

Run this outside the source checkout after installing the wheel. The check reads
the distribution's generated ``top_level.txt`` instead of maintaining a module
allowlist, then recursively imports package contents without making network calls.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import importlib
from importlib import metadata
import json
import pkgutil
from types import ModuleType
from typing import Callable, Iterable, Protocol


class DistributionLike(Protocol):
    """Small metadata surface needed by the import check."""

    def read_text(self, filename: str) -> str | None:
        """Return generated distribution metadata text."""


@dataclass(frozen=True)
class ImportFailure:
    """One module that could not be imported."""

    module: str
    error_type: str
    message: str


@dataclass(frozen=True)
class ImportCheckResult:
    """Deterministic result for one installed distribution."""

    distribution: str
    imported_modules: tuple[str, ...]
    failures: tuple[ImportFailure, ...]

    @property
    def passed(self) -> bool:
        """Return whether every discovered module imported."""

        return not self.failures

    def to_dict(self) -> dict[str, object]:
        """Serialize the result for CI output."""

        return {
            "distribution": self.distribution,
            "passed": self.passed,
            "imported_modules": list(self.imported_modules),
            "failures": [
                {
                    "module": failure.module,
                    "error_type": failure.error_type,
                    "message": failure.message,
                }
                for failure in self.failures
            ],
        }


def _top_level_names(distribution: DistributionLike) -> tuple[str, ...]:
    """Read and validate the distribution's generated top-level import names."""

    payload = distribution.read_text("top_level.txt")
    if payload is None:
        raise ValueError("installed distribution is missing top_level.txt")

    names = tuple(
        sorted(
            {
                line.strip()
                for line in payload.splitlines()
                if line.strip() and line.strip().isidentifier()
            }
        )
    )
    if not names:
        raise ValueError("installed distribution declares no importable top-level modules")
    return names


def _walk_module_names(module: ModuleType) -> Iterable[str]:
    """Yield recursive package members without importing them during discovery."""

    package_path = getattr(module, "__path__", None)
    if package_path is None:
        return ()
    return tuple(
        sorted(
            item.name
            for item in pkgutil.walk_packages(
                package_path,
                prefix=f"{module.__name__}.",
            )
        )
    )


def check_distribution_imports(
    distribution_name: str,
    *,
    distribution_getter: Callable[[str], DistributionLike] = metadata.distribution,
    importer: Callable[[str], ModuleType] = importlib.import_module,
    walker: Callable[[ModuleType], Iterable[str]] = _walk_module_names,
) -> ImportCheckResult:
    """Import every generated top-level module and recursively discovered member."""

    distribution = distribution_getter(distribution_name)
    pending = list(_top_level_names(distribution))
    seen: set[str] = set()
    imported: list[str] = []
    failures: list[ImportFailure] = []

    while pending:
        module_name = pending.pop(0)
        if module_name in seen:
            continue
        seen.add(module_name)
        try:
            module = importer(module_name)
        except Exception as exc:  # noqa: BLE001 - the audit must report all import failures
            failures.append(
                ImportFailure(
                    module=module_name,
                    error_type=type(exc).__name__,
                    message=str(exc),
                )
            )
            continue

        imported.append(module_name)
        try:
            discovered = tuple(walker(module))
        except Exception as exc:  # noqa: BLE001 - discovery failures are audit failures
            failures.append(
                ImportFailure(
                    module=f"{module_name}.__discovery__",
                    error_type=type(exc).__name__,
                    message=str(exc),
                )
            )
            continue
        pending.extend(name for name in discovered if name not in seen)
        pending.sort()

    return ImportCheckResult(
        distribution=distribution_name,
        imported_modules=tuple(imported),
        failures=tuple(failures),
    )


def main() -> int:
    """Run the installed-distribution import audit."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--distribution", default="autopredict")
    args = parser.parse_args()
    result = check_distribution_imports(args.distribution)
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
