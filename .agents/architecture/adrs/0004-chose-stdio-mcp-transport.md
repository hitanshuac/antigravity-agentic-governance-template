# ADR-0004: Chose stdio MCP transport over HTTP

## Status
Accepted

## Context
We need a way to expose governance tools (like Ponytail checking and environment awareness) to local IDE agents (Cursor, Claude Code) without requiring complex networking or Docker containers for the local development environment.

## Decision
We chose the `stdio` (Standard I/O) transport for the Model Context Protocol (MCP) server instead of SSE/HTTP.

## Consequences
- Zero network overhead or port conflicts.
- Local agents can directly spawn the Python process.
- Slightly harder to debug manually without a client compared to HTTP.
