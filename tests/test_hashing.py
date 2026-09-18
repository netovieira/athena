from __future__ import annotations

from athena.hashing import hash_file, hash_text


def test_hash_text_deterministic():
    assert hash_text("hello") == hash_text("hello")


def test_hash_text_differs_on_different_content():
    assert hash_text("hello") != hash_text("world")


def test_hash_text_known_sha256():
    # sha256("") is a well-known constant value.
    assert hash_text("") == (
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )


def test_hash_file_deterministic_same_content(tmp_path):
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.txt"
    file_a.write_text("same content", encoding="utf-8")
    file_b.write_text("same content", encoding="utf-8")

    assert hash_file(file_a) == hash_file(file_b)


def test_hash_file_differs_on_different_content(tmp_path):
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.txt"
    file_a.write_text("content one", encoding="utf-8")
    file_b.write_text("content two", encoding="utf-8")

    assert hash_file(file_a) != hash_file(file_b)


def test_hash_file_matches_hash_text_for_utf8_content(tmp_path):
    file_path = tmp_path / "a.txt"
    file_path.write_text("hello", encoding="utf-8")

    assert hash_file(file_path) == hash_text("hello")


def test_hash_file_reads_large_content_in_chunks(tmp_path):
    file_path = tmp_path / "big.bin"
    # Bigger than the 65536-byte chunk size used internally.
    content = b"x" * 200_000
    file_path.write_bytes(content)

    import hashlib

    assert hash_file(file_path) == hashlib.sha256(content).hexdigest()
