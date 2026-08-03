import asyncio
import logging
from pathlib import Path

import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("antigravity-mcp-server")

# Initialize the MCP Server
server = Server("antigravity-governance")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available governance tools to connected agents.
    """
    return [
        types.Tool(
            name="check_ponytail_compliance",
            description=(
                "Run the Ponytail 7-step anti-over-engineering ladder check "
                "(DietrichGebert/ponytail). Scores complexity based on new "
                "dependencies, files touched, and existing dependency count."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "The task or proposed change the agent wants to implement.",
                    },
                    "workspace_root": {
                        "type": "string",
                        "description": "Absolute path to the project root directory.",
                    },
                    "proposed_new_dependencies": {
                        "type": "integer",
                        "description": "Number of NEW external dependencies being added.",
                    },
                    "files_touched": {
                        "type": "integer",
                        "description": "Number of files this change will create or modify.",
                    },
                },
                "required": ["task_description"],
            },
        ),
        types.Tool(
            name="verify_environment_awareness",
            description="Verify agent scanned the workspace for environment files before executing.",
            inputSchema={
                "type": "object",
                "properties": {
                    "detected_ecosystem": {
                        "type": "string",
                        "description": "The ecosystem detected (e.g., node, python, go, rust).",
                    },
                    "workspace_root": {
                        "type": "string",
                        "description": "Absolute path to the project root directory.",
                    },
                },
                "required": ["detected_ecosystem"],
            },
        ),
        types.Tool(
            name="run_eval_scorecard",
            description="Run the governance evaluation harness and return the scorecard.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests from the agent.
    """
    if name == "check_ponytail_compliance":
        # Ponytail 7-Step Ladder (DietrichGebert/ponytail)
        # Before writing code, the agent stops at the first rung that holds:
        # 1. Does this need to exist?       → no: skip it (YAGNI)
        # 2. Already in this codebase?       → reuse it, don't rewrite
        # 3. Stdlib does it?                 → use it
        # 4. Native platform feature?        → use it
        # 5. Installed dependency?           → use it
        # 6. One line?                       → one line
        # 7. Only then: the minimum that works
        task = arguments.get("task_description", "Unknown task")
        workspace = Path(arguments.get("workspace_root", "."))
        proposed_new_deps = arguments.get("proposed_new_dependencies", 0)
        files_touched = arguments.get("files_touched", 0)
        logger.info(f"Ponytail Ladder Check for: {task}")

        # Score complexity signals
        score = 0
        findings = []

        # Signal 1: New external dependencies (each new dep = +2)
        if proposed_new_deps > 0:
            score += proposed_new_deps * 2
            findings.append(
                f"Rung 5 FAIL: {proposed_new_deps} new dependency(ies) proposed. "
                f"Can stdlib or an installed dep handle this?"
            )

        # Signal 2: Files touched (>5 files = likely over-scoped)
        if files_touched > 5:
            score += (files_touched - 5)
            findings.append(
                f"Rung 7 WARNING: {files_touched} files touched. "
                f"Minimum-that-works rarely needs >5 files."
            )

        # Signal 3: Existing dependency count (bloat detector)
        dep_count = 0
        req_file = workspace / "requirements.txt"
        pkg_json = workspace / "package.json"
        if req_file.exists():
            lines = req_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            dep_count = sum(1 for line in lines if line.strip() and not line.strip().startswith("#"))
        elif pkg_json.exists():
            import json
            try:
                pkg = json.loads(pkg_json.read_text(encoding="utf-8"))
                dep_count = len(pkg.get("dependencies", {})) + len(pkg.get("devDependencies", {}))
            except (json.JSONDecodeError, KeyError):
                pass
        if dep_count > 30:
            score += 1
            findings.append(
                f"Project already has {dep_count} dependencies. "
                f"Adding more increases maintenance surface."
            )

        # Classify result using the ladder
        if score == 0:
            summary = (
                "Ponytail Ladder PASSED (Score 0): Proceed with minimalist "
                "implementation. Remember: lazy about the solution, never about "
                "reading the code first."
            )
        elif score <= 2:
            summary = (
                f"Ponytail Ladder REVIEW (Score {score}): Moderate complexity "
                f"detected. Walk the ladder — can you solve this at a higher rung "
                f"(stdlib, platform feature, existing dep)?\n"
                + "\n".join(f"  • {f}" for f in findings)
            )
        else:
            summary = (
                f"Ponytail Ladder HALT (Score {score}): High complexity. "
                f"Justify this to the user before proceeding.\n"
                + "\n".join(f"  • {f}" for f in findings)
                + "\n\nThe 7-Step Ladder (stop at the first rung that holds):\n"
                "  1. Does this need to exist? (YAGNI)\n"
                "  2. Already in this codebase? (reuse)\n"
                "  3. Stdlib does it? (use it)\n"
                "  4. Native platform feature? (use it)\n"
                "  5. Installed dependency? (use it)\n"
                "  6. One line? (write one line)\n"
                "  7. Only then: the minimum that works"
            )

        return [types.TextContent(type="text", text=summary)]

    elif name == "verify_environment_awareness":
        ecosystem = arguments.get("detected_ecosystem", "Unknown")
        workspace = Path(arguments.get("workspace_root", "."))
        logger.info(f"Environment awareness verified for: {ecosystem} at {workspace}")

        # Verify actual files exist relative to workspace root
        has_python = (workspace / "requirements.txt").exists() or (workspace / "pyproject.toml").exists()
        has_node = (workspace / "package.json").exists()
        has_go = (workspace / "go.mod").exists()

        detected_files = []
        if has_python:
            detected_files.append("Python")
        if has_node:
            detected_files.append("Node")
        if has_go:
            detected_files.append("Go")

        return [
            types.TextContent(
                type="text",
                text=(
                    f"Environment verified: {ecosystem}. "
                    f"Actual detected: {', '.join(detected_files) if detected_files else 'None'}. "
                    f"You may proceed using native tools for this ecosystem."
                ),
            )
        ]

    elif name == "run_eval_scorecard":
        logger.info("Running eval scorecard...")
        try:
            process = await asyncio.create_subprocess_exec(
                "python", "-m", "tools.governance_eval.cli", "analyze",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                return [types.TextContent(type="text", text=f"Eval harness failed: {stderr.decode()}")]
            # Try to read the scorecard
            if Path("governance_scorecard.md").exists():
                scorecard = Path("governance_scorecard.md").read_text(encoding="utf-8")
                return [types.TextContent(type="text", text=f"Eval Harness ran successfully.\n\n{scorecard}")]
            return [types.TextContent(type="text", text=f"Eval ran, but no scorecard found. Stdout: {stdout.decode()}")]
        except FileNotFoundError:
            return [types.TextContent(type="text", text="Eval harness failed: python not found on PATH")]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """
    Run the MCP server over standard I/O (stdio).
    This allows local agents (like Cursor, Claude Code) to spawn this Python process
    and communicate with it directly without networking overhead.
    """
    logger.info("Starting Antigravity Governance MCP Server...")
    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="antigravity-governance",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
