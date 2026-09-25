from __future__ import annotations

import sys
from pathlib import Path

from toposort_app.resources import resource_path


def test_source_manual_resource_exists() -> None:
    assert resource_path("docs/使用说明.md").is_file()


def test_frozen_resources_use_bundle_then_external_override(tmp_path: Path, monkeypatch) -> None:
    bundle = tmp_path / "application"
    internal = bundle / "_internal"
    bundled_manual = internal / "docs" / "使用说明.md"
    bundled_manual.parent.mkdir(parents=True)
    bundled_manual.write_text("bundled", encoding="utf-8")
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(internal), raising=False)
    monkeypatch.setattr(sys, "executable", str(bundle / "app.exe"))

    assert resource_path("docs/使用说明.md") == bundled_manual

    external_manual = bundle / "docs" / "使用说明.md"
    external_manual.parent.mkdir(parents=True)
    external_manual.write_text("external", encoding="utf-8")
    assert resource_path("docs/使用说明.md") == external_manual
