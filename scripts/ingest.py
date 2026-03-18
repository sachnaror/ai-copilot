from pathlib import Path

from app.rag.chunking import chunk_text


def main() -> None:
    source = Path("data/sample.pdf")
    # In production, parse PDF/Jira/Slack and push chunks to Mosaic Vector Search.
    text = source.read_text(encoding="utf-8") if source.exists() else "No sample data"
    chunks = chunk_text(text, chunk_size=80)
    print(f"Prepared {len(chunks)} chunks for ingestion to Databricks Vector Search")


if __name__ == "__main__":
    main()
