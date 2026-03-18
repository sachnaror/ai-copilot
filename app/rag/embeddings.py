from typing import Sequence


def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    """Placeholder embedding function. Use Databricks embedding endpoint in production."""
    return [[float(len(t) % 13), float(len(t) % 17), float(len(t) % 19)] for t in texts]
