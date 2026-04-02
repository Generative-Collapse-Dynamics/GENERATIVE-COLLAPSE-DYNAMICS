"""UMCP MCP Server — the tightest nozzle.

Exposes GCD-native operations as MCP tools so that any AI model
interacts exclusively through the frozen contract. The model never
touches raw constants — F, ω, S, C, κ, IC are return values from
functions it cannot modify. Symbol capture becomes structurally
impossible.

Run:
    python -m umcp_mcp            # stdio transport (default)
    python -m umcp_mcp --sse      # SSE transport on port 8765

Or via entry point:
    umcp-mcp
    umcp-mcp --sse
"""

from __future__ import annotations

__version__ = "1.0.0"
