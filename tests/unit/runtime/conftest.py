"""Fixtures for runtime provider unit tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


class _FakeBox:
    """Stand-in for boxd.aio.Box used by tests."""

    def __init__(self, name: str = "agent", vm_id: str = "vm-1"):
        self.id = vm_id
        self.name = name
        self.image = "ubuntu:latest"
        self.public_ip = "1.2.3.4"
        self.status = "running"
        self.url = f"https://{name}.boxd.sh"
        self.boot_time_ms = 2000
        # All async methods that the provider may call:
        self.exec = AsyncMock()
        self.write_file = AsyncMock()
        self.read_file = AsyncMock(return_value=b"")
        self.destroy = AsyncMock()
        self.suspend = AsyncMock()
        self.resume = AsyncMock()
        # `stream_logs` is set by tests that exercise log streaming.
        self.stream_logs = MagicMock()


class _FakeBoxService:
    def __init__(self):
        self.create = AsyncMock()
        self.get = AsyncMock()
        self.list = AsyncMock(return_value=[])
        self.fork = AsyncMock()


class _FakeCompute:
    """Stand-in for boxd.aio.Compute used as an async context manager."""

    def __init__(self):
        self.box = _FakeBoxService()
        self.template = MagicMock()
        self.disk = MagicMock()
        self.domain = MagicMock()
        self.network = MagicMock()
        self.token = MagicMock()
        self.close = AsyncMock()
        self.whoami = AsyncMock()
        self.config = AsyncMock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        await self.close()


@pytest.fixture
def fake_box():
    """A fresh _FakeBox per test."""
    return _FakeBox()


@pytest.fixture
def fake_compute(fake_box):
    """A fresh _FakeCompute per test, wired so .box.create returns fake_box."""
    c = _FakeCompute()
    c.box.create.return_value = fake_box
    c.box.get.return_value = fake_box
    return c


@pytest.fixture
def mock_boxd(monkeypatch, fake_compute):
    """Patch boxd_provider._make_compute to return `fake_compute`."""
    import bindu.runtime.boxd_provider as bp

    monkeypatch.setattr(bp, "_make_compute", lambda **kw: fake_compute)
    return fake_compute
