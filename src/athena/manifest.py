from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class Manifest:
    """
    Cache incremental: guarda o hash de cada arquivo/pasta já
    indexado, para que uma nova rodada só re-resuma o que mudou.
    """

    def __init__(self, path: Path) -> None:
        self._path = path
        self._entries: dict[str, dict[str, Any]] = {}
        self._touched: set[str] = set()
        self._load()

    def _load(self) -> None:

        if not self._path.exists():
            return

        try:
            data = json.loads(
                self._path.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            return

        self._entries = data.get("entries", {})

    def get_hash(self, relative_path: str) -> str | None:
        entry = self._entries.get(relative_path)
        return entry["hash"] if entry else None

    def mark(
        self,
        relative_path: str,
        content_hash: str,
        summary_path: str,
        node_type: str,
    ) -> None:

        self._entries[relative_path] = {
            "hash": content_hash,
            "summary_path": summary_path,
            "type": node_type,
        }
        self._touched.add(relative_path)

    def prune_untouched(self) -> list[dict[str, Any]]:
        """
        Remove entradas de arquivos/pastas que não existem mais no
        projeto (não foram tocadas nesta rodada). Retorna as entradas
        removidas (com "summary_path"), para o chamador apagar os
        resumos órfãos em disco.
        """

        stale_paths = [
            path
            for path in self._entries
            if path not in self._touched
        ]

        removed: list[dict[str, Any]] = []

        for path in stale_paths:
            removed.append(self._entries.pop(path))

        return removed

    def save(self) -> None:

        self._path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = {
            "version": 1,
            "entries": self._entries,
        }

        self._path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
