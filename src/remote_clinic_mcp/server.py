"""Remote MCP server running over Streamable HTTP."""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta, timezone
from typing import Any

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from .catalog import check_requirements, get_preparation, list_preparations

GUATEMALA_TIMEZONE = timezone(-timedelta(hours=6), name="America/Guatemala")

mcp = FastMCP(
    "Remote Clinic Preparation Catalog",
    instructions="Preparation requirements catalog for laboratory exams.",
    host="0.0.0.0",
    port=int(os.getenv("PORT", "8080")),
    streamable_http_path="/mcp",
    stateless_http=True,
    json_response=True,
)


@mcp.tool()
def list_lab_preparations(category: str | None = None) -> dict[str, Any]:
    """List laboratory preparation policies by optional category."""
    return list_preparations(category)


@mcp.tool()
def get_lab_preparation(test_code: str) -> dict[str, Any]:
    """Get the preparation policy for one laboratory test code."""
    return get_preparation(test_code)


@mcp.tool()
def check_lab_preparation(
    test_code: str,
    fasting_hours: float = 0,
    hours_since_alcohol: float | None = None,
    hours_since_strenuous_exercise: float | None = None,
) -> dict[str, Any]:
    """Check patient preparation facts against test requirements."""
    return check_requirements(
        test_code,
        fasting_hours,
        hours_since_alcohol,
        hours_since_strenuous_exercise,
    )


@mcp.tool()
def get_remote_server_time() -> dict[str, str]:
    """Return current UTC and local Guatemala timestamps."""
    now = datetime.now(UTC)
    return {
        "utc": now.isoformat(),
        "guatemala": now.astimezone(GUATEMALA_TIMEZONE).isoformat(),
        "transport": "streamable-http",
    }


@mcp.custom_route("/health", methods=["GET"])
async def health(_: Request) -> JSONResponse:
    """Return a small health response for the cloud platform."""
    return JSONResponse({"status": "ok", "server": "remote-clinic-mcp"})


def main() -> None:
    """Serve MCP over Streamable HTTP."""
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
