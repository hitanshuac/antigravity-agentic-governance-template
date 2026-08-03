import pytest

try:
    from mcp.server.fastmcp import FastMCP  # noqa: F401
    HAS_MCP = True
except ImportError:
    HAS_MCP = False

@pytest.mark.skipif(not HAS_MCP, reason="MCP package not installed")
def test_mcp_server_initialization():
    """Verify the MCP server initializes correctly."""
    # Assuming standard fastmcp or equivalent structure
    from src.antigravity.capabilities.mcp.server import server

    assert server is not None
    assert server.name == "antigravity-governance"
