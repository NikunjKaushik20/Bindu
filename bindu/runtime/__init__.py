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

# Side-effect imports: providers register themselves on import. Boxd's
# deploy()/health()/etc. lazily import the boxd SDK, so importing
# bindu.runtime does not require `boxd` to be installed.
from bindu.runtime import in_process as _in_process  # noqa: F401, E402
from bindu.runtime import boxd_provider as _boxd_provider  # noqa: F401, E402

__all__ = [
    "RuntimeHandle",
    "RuntimeProvider",
    "UnknownProviderError",
    "register_provider",
    "get_provider",
    "RuntimeConfig",
    "RuntimeConfigError",
]
