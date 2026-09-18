from __future__ import annotations

import json

from athena.manifest import Manifest


def test_get_hash_returns_none_when_empty(tmp_path):
    manifest = Manifest(tmp_path / "manifest.json")

    assert manifest.get_hash("some/file.py") is None


def test_mark_then_get_hash_returns_stored_hash(tmp_path):
    manifest = Manifest(tmp_path / "manifest.json")

    manifest.mark("some/file.py", "abc123", "tree/some/file.py.md", "file")

    assert manifest.get_hash("some/file.py") == "abc123"


def test_prune_untouched_removes_only_untouched_entries(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    manifest = Manifest(manifest_path)
    manifest.mark("kept.py", "hash-kept", "tree/kept.py.md", "file")
    manifest.mark("removed.py", "hash-removed", "tree/removed.py.md", "file")
    manifest.save()

    reloaded = Manifest(manifest_path)
    reloaded.mark("kept.py", "hash-kept", "tree/kept.py.md", "file")
    # "removed.py" is not marked this round -> it is stale.

    removed = reloaded.prune_untouched()

    assert len(removed) == 1
    assert removed[0]["summary_path"] == "tree/removed.py.md"
    assert reloaded.get_hash("kept.py") == "hash-kept"
    assert reloaded.get_hash("removed.py") is None


def test_prune_untouched_returns_empty_when_all_touched(tmp_path):
    manifest = Manifest(tmp_path / "manifest.json")
    manifest.mark("a.py", "hash-a", "tree/a.py.md", "file")

    assert manifest.prune_untouched() == []


def test_save_then_load_round_trip(tmp_path):
    manifest_path = tmp_path / "sub" / "manifest.json"
    manifest = Manifest(manifest_path)
    manifest.mark("dir/file.py", "deadbeef", "tree/dir/file.py.md", "file")
    manifest.save()

    assert manifest_path.exists()

    reloaded = Manifest(manifest_path)
    assert reloaded.get_hash("dir/file.py") == "deadbeef"


def test_save_creates_parent_directories(tmp_path):
    manifest_path = tmp_path / "a" / "b" / "c" / "manifest.json"
    manifest = Manifest(manifest_path)
    manifest.mark("x", "y", "tree/x.md", "file")

    manifest.save()

    assert manifest_path.exists()


def test_load_ignores_missing_file(tmp_path):
    manifest = Manifest(tmp_path / "does-not-exist.json")

    assert manifest.get_hash("anything") is None


def test_load_recovers_from_corrupted_json(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text("{not valid json", encoding="utf-8")

    manifest = Manifest(manifest_path)

    assert manifest.get_hash("anything") is None
    # Manifest still usable after a corrupted load.
    manifest.mark("a", "b", "tree/a.md", "file")
    assert manifest.get_hash("a") == "b"


def test_save_writes_valid_json_with_version(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    manifest = Manifest(manifest_path)
    manifest.mark("a", "hash-a", "tree/a.md", "file")

    manifest.save()

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data["version"] == 1
    assert data["entries"]["a"]["hash"] == "hash-a"
    assert data["entries"]["a"]["type"] == "file"
