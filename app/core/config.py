from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Enterprise AI Knowledge Copilot"
    env: str = "dev"

    databricks_host: str = ""
    databricks_token: str = ""
    databricks_workspace_url: str = ""
    databricks_model_serving_endpoint: str = ""
    databricks_vector_search_endpoint: str = ""
    databricks_vector_search_index: str = ""
    databricks_sql_warehouse_id: str = ""

    mlflow_tracking_uri: str = ""
    mlflow_experiment_name: str = "enterprise-ai-copilot"

    pgvector_dsn: str = ""

    jira_base_url: str = ""
    jira_api_token: str = ""

    jwt_secret_key: str = "change-me-demo-secret-key-32-bytes-min"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "enterprise-ai-copilot"
    jwt_audience: str = "enterprise-users"
    jwt_access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
