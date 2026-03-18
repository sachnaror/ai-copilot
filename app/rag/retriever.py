from app.core.databricks import DatabricksClient, RetrievalResult


class EnterpriseRetriever:
    def __init__(self) -> None:
        self.dbx = DatabricksClient()

    def retrieve(self, query: str, top_k: int = 4) -> list[RetrievalResult]:
        return self.dbx.vector_search(query=query, k=top_k)
