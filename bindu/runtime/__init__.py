"""Runtime provider abstraction for bindu agents.

A ``RuntimeProvider`` controls *where* a bindu agent's process runs.
The default (``InProcessRuntimeProvider``) runs the agent in the host
process, matching today's behavior. ``BoxdRuntimeProvider`` runs the
agent inside a boxd microVM.
"""

from bindu.runtime.base import (
    RuntimeHandle,
    RuntimeProvider,
    UnknownProviderError,
    get_provider,
    register_provider,
)
from bindu.runtime.config import RuntimeConfig, RuntimeConfigError

__all__ = [
    "RuntimeHandle",
    "RuntimeProvider",
    "UnknownProviderError",
    "register_provider",
    "get_provider",
    "RuntimeConfig",
    "RuntimeConfigError",
]
