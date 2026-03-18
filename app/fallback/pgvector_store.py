from typing import Any


class PGVectorFallbackStore:
    """Fallback retrieval skeleton for non-Databricks environments."""

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    def search(self, query: str, k: int = 4) -> list[dict[str, Any]]:
        # Placeholder for psycopg + pgvector search implementation.
        return [{"source": "pgvector://fallback", "content": f"Fallback for: {query}", "score": 0.5}]
