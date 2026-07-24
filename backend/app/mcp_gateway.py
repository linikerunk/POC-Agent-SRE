"""FastMCP gateway exposing the SRE agent's tools to MCP clients
(Claude Desktop, Claude Code, etc.).

Run standalone (stdio transport):
    python -m app.mcp_gateway
"""
from fastmcp import FastMCP

from app.services import agent_service

mcp = FastMCP("SRE Agent Gateway")


@mcp.tool()
def diagnose(source: str, logs: str) -> dict:
    """Analyze a log/metric snippet and return severity, root cause, and
    recommended actions. `source` identifies where the signal came from,
    e.g. 'nginx', 'k8s-pod', 'postgres'."""
    response = agent_service.diagnose(source, logs)
    return response.model_dump(mode="json")


@mcp.tool()
def list_incidents() -> list[dict]:
    """List all incidents recorded so far, most recent first."""
    return [i.model_dump(mode="json") for i in reversed(agent_service.list_incidents())]


if __name__ == "__main__":
    mcp.run()
