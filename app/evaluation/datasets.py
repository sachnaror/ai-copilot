from dataclasses import dataclass


@dataclass
class GoldenSample:
    question: str
    expected_keywords: list[str]


class GoldenDataset:
    @staticmethod
    def default_samples() -> list[GoldenSample]:
        return [
            GoldenSample(
                question="What is the incident communication policy from docs?",
                expected_keywords=["incident", "Jira", "30 minutes"],
            ),
            GoldenSample(
                question="Fetch Jira tickets for engineering project.",
                expected_keywords=["jira", "project", "ticket"],
            ),
            GoldenSample(
                question="Run SQL to check latest timestamp.",
                expected_keywords=["sql", "select", "ts"],
            ),
        ]
