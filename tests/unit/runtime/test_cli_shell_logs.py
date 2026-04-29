"""Tests for ``bindu shell <agent>`` and ``bindu logs <agent>``."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_logs_streams_to_stdout(capsys):
    """`bindu logs my-agent` should pipe VM logs to stdout."""
    from bindu.cli import _handle_logs

    fake_box = MagicMock()
    chunks = [b"hello\n", b"world\n"]

    async def fake_stream(follow=True):
        for c in chunks:
            yield c

    fake_box.stream_logs = fake_stream

    fake_compute = MagicMock()
    fake_compute.box.get = AsyncMock(return_value=fake_box)
    fake_compute.__aenter__ = AsyncMock(return_value=fake_compute)
    fake_compute.__aexit__ = AsyncMock()

    with patch("bindu.cli._make_compute", return_value=fake_compute):
        await _handle_logs("my-agent", follow=False)

    out = capsys.readouterr().out
    assert "hello" in out
    assert "world" in out


@pytest.mark.asyncio
async def test_shell_calls_exec_bash():
    """`bindu shell my-agent` should exec `bash` interactively on the VM."""
    from bindu.cli import _handle_shell

    fake_box = MagicMock()
    fake_box.exec = AsyncMock()

    fake_compute = MagicMock()
    fake_compute.box.get = AsyncMock(return_value=fake_box)
    fake_compute.__aenter__ = AsyncMock(return_value=fake_compute)
    fake_compute.__aexit__ = AsyncMock()

    with patch("bindu.cli._make_compute", return_value=fake_compute):
        await _handle_shell("my-agent")

    fake_box.exec.assert_awaited_once()
    args = fake_box.exec.await_args
    assert "bash" in args.args
    assert args.kwargs.get("interactive") is True
