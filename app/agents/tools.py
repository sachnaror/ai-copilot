from typing import Any

from app.core.databricks import DatabricksClient


dbx = DatabricksClient()


def fetch_jira_tickets(project_key: str) -> dict[str, Any]:
    return dbx.run_uc_function("catalog.tools.fetch_jira_tickets", {"project_key": project_key})


def run_sql_query(sql: str) -> dict[str, Any]:
    return dbx.run_uc_function("catalog.tools.run_sql_query", {"sql": sql})


def trigger_internal_api(api_name: str, body: dict[str, Any]) -> dict[str, Any]:
    return dbx.run_uc_function(
        "catalog.tools.trigger_internal_api",
        {"api_name": api_name, "body": body},
    )


def allowed_tools_for_roles(roles: list[str]) -> set[str]:
    role_to_tools = {
        "viewer": set(),
        "analyst": {"fetch_jira_tickets", "run_sql_query"},
        "operator": {"fetch_jira_tickets", "run_sql_query", "trigger_internal_api"},
        "admin": {"fetch_jira_tickets", "run_sql_query", "trigger_internal_api"},
    }
    tools: set[str] = set()
    for role in roles:
        tools.update(role_to_tools.get(role, set()))
    return tools
