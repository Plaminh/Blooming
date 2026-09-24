"""Shared setup for database-free unit tests."""

import pytest


@pytest.fixture(autouse=True)
def no_carried_work(monkeypatch):
    """Unit tests fake the database, so no deferred or recurring work exists.

    Tests of carry-over behaviour patch ``carried_tasks`` themselves.
    """

    async def none(*_args, **_kwargs):
        return []

    monkeypatch.setattr("app.ai.handlers.planner.carried_tasks", none)
