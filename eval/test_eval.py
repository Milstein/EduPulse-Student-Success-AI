"""Evaluation tests for EduPulse using ADK AgentEvaluator."""

import pathlib

import dotenv
import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()


@pytest.mark.asyncio
async def test_edupulse_student_routing():
    """Test that EduPulse correctly routes a student query."""
    agent_name = "root_agent"
    data_path = str(pathlib.Path(__file__).parent / "data")

    await AgentEvaluator.evaluate(
        agent_name,
        data_path,
        eval_set_name="edupulse_routing_evalset",
        num_runs=1,
    )
