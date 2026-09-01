from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .models import RetrievedDocument


TOKEN_RE = re.compile(r"[a-zA-Z_]+|\d+|[\u4e00-\u9fff]+")


@dataclass(frozen=True)
class KnowledgeDocument:
    id: str
    title: str
    tags: list[str]
    content: str


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for chunk in TOKEN_RE.findall(text.lower()):
        if re.fullmatch(r"[\u4e00-\u9fff]+", chunk):
            tokens.extend(chunk)
            tokens.extend(chunk[i : i + 2] for i in range(max(0, len(chunk) - 1)))
        else:
            tokens.append(chunk)
    return tokens


class KnowledgeBase:
    def __init__(self, path: Path):
        self.path = path
        self.documents = self._load(path)
        self._doc_vectors: dict[str, dict[str, float]] = {}
        self._idf: dict[str, float] = {}
        self._build_index()

    @staticmethod
    def _load(path: Path) -> list[KnowledgeDocument]:
        docs: list[KnowledgeDocument] = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                item = json.loads(line)
                docs.append(
                    KnowledgeDocument(
                        id=item["id"],
                        title=item["title"],
                        tags=item.get("tags", []),
                        content=item["content"],
                    )
                )
        return docs

    def _build_index(self) -> None:
        doc_token_counts: dict[str, Counter[str]] = {}
        document_frequency: Counter[str] = Counter()

        for doc in self.documents:
            text = f"{doc.title} {' '.join(doc.tags)} {doc.content}"
            counts = Counter(tokenize(text))
            doc_token_counts[doc.id] = counts
            document_frequency.update(counts.keys())

        doc_count = max(len(self.documents), 1)
        self._idf = {
            token: math.log((1 + doc_count) / (1 + frequency)) + 1
            for token, frequency in document_frequency.items()
        }

        for doc in self.documents:
            counts = doc_token_counts[doc.id]
            total = sum(counts.values()) or 1
            self._doc_vectors[doc.id] = {
                token: (count / total) * self._idf.get(token, 1.0)
                for token, count in counts.items()
            }

    def _query_vector(self, query: str) -> dict[str, float]:
        counts = Counter(tokenize(query))
        total = sum(counts.values()) or 1
        return {token: (count / total) * self._idf.get(token, 1.0) for token, count in counts.items()}

    @staticmethod
    def _cosine(left: dict[str, float], right: dict[str, float]) -> float:
        if not left or not right:
            return 0.0
        numerator = sum(value * right.get(token, 0.0) for token, value in left.items())
        left_norm = math.sqrt(sum(value * value for value in left.values()))
        right_norm = math.sqrt(sum(value * value for value in right.values()))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return numerator / (left_norm * right_norm)

    def search(self, query: str, top_k: int = 4) -> list[RetrievedDocument]:
        query_vector = self._query_vector(query)
        scored = []
        for doc in self.documents:
            score = self._cosine(query_vector, self._doc_vectors[doc.id])
            tag_bonus = sum(0.03 for tag in doc.tags if tag.lower() in query.lower())
            scored.append((score + tag_bonus, doc))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            RetrievedDocument(
                id=doc.id,
                title=doc.title,
                tags=doc.tags,
                content=doc.content,
                score=round(score, 4),
            )
            for score, doc in scored[:top_k]
        ]
