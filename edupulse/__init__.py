from . import config

try:
    import agentops  # noqa: E402

    if config.AGENTOPS_API_KEY:
        agentops.init(
            api_key=config.AGENTOPS_API_KEY,
            default_tags=["edupulse", "adk", "cloud-run"],
        )
except ImportError:
    pass

from .agent import root_agent as root_agent  # noqa: E402, F401
