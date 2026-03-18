import asyncio

from app.agents.agent import EnterpriseCopilotAgent
from app.evaluation.datasets import GoldenDataset
from app.evaluation.evaluator import evaluate_run


async def main() -> None:
    agent = EnterpriseCopilotAgent()
    samples = GoldenDataset.default_samples()
    result = await evaluate_run(agent=agent, samples=samples, run_name="cli-eval")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
