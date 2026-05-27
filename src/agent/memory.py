from __future__ import annotations

from collections import defaultdict


class CaseMemory:
    def __init__(self) -> None:
        self._memory = defaultdict(list)

    def remember(self, claim_id: str, note: str) -> None:
        self._memory[claim_id].append(note)

    def recall(self, claim_id: str) -> list[str]:
        return list(self._memory.get(claim_id, []))
