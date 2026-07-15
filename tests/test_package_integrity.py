"""Tests for installed-distribution import integrity helpers."""

from __future__ import annotations

from types import ModuleType

from scripts.check_package_imports import check_distribution_imports


class _FakeDistribution:
    def __init__(self, top_level: str | None) -> None:
        self.top_level = top_level

    def read_text(self, filename: str) -> str | None:
        assert filename == "top_level.txt"
        return self.top_level


def test_import_check_imports_declared_top_level_modules() -> None:
    imported: list[str] = []

    def importer(name: str) -> ModuleType:
        imported.append(name)
        return ModuleType(name)

    result = check_distribution_imports(
        "fixture",
        distribution_getter=lambda _: _FakeDistribution("second\nfirst\n"),
        importer=importer,
    )

    assert result.passed is True
    assert result.imported_modules == ("first", "second")
    assert imported == ["first", "second"]


def test_import_check_reports_a_deliberately_broken_module() -> None:
    def importer(name: str) -> ModuleType:
        if name == "broken_module":
            raise RuntimeError("deliberate import failure")
        return ModuleType(name)

    result = check_distribution_imports(
        "fixture",
        distribution_getter=lambda _: _FakeDistribution("working_module\nbroken_module\n"),
        importer=importer,
    )

    assert result.passed is False
    assert result.imported_modules == ("working_module",)
    assert len(result.failures) == 1
    assert result.failures[0].module == "broken_module"
    assert result.failures[0].error_type == "RuntimeError"
    assert result.failures[0].message == "deliberate import failure"


def test_import_check_rejects_missing_top_level_metadata() -> None:
    try:
        check_distribution_imports(
            "fixture",
            distribution_getter=lambda _: _FakeDistribution(None),
        )
    except ValueError as exc:
        assert "missing top_level.txt" in str(exc)
    else:
        raise AssertionError("missing metadata unexpectedly passed")


def test_import_check_reports_recursive_discovery_failure() -> None:
    result = check_distribution_imports(
        "fixture",
        distribution_getter=lambda _: _FakeDistribution("broken_package\n"),
        importer=lambda name: ModuleType(name),
        walker=lambda _: (_ for _ in ()).throw(RuntimeError("discovery failed")),
    )

    assert result.passed is False
    assert result.imported_modules == ("broken_package",)
    assert len(result.failures) == 1
    assert result.failures[0].module == "broken_package.__discovery__"
    assert result.failures[0].message == "discovery failed"
