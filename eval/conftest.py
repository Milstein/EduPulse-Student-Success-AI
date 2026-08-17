"""Shared fixtures for EduPulse eval tests."""

import dotenv
import pytest

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()
