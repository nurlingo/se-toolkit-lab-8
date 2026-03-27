# Lab 8 Report

## Task 1A — Bare agent

Agent responds to general questions. When asked about LMS labs, it says it doesn't know (no tools yet).

## Task 1B — Agent with LMS tools

After adding MCP tools, the agent returns real lab names from the backend.

## Task 1C — Skill prompt

With the skill prompt, the agent asks which lab when the user says "show me the scores" without specifying.

## Task 2A — Deployed agent

Nanobot gateway started successfully as a Docker service. Logs show MCP tools registered.

## Task 2B — Web client

Flutter client accessible at /flutter. WebSocket connection works with access key.

## Task 3A — Structured logging

Backend emits structured JSON logs with OTEL trace correlation visible in docker compose logs.

## Task 3B — Traces

VictoriaTraces shows request traces with span hierarchy and timing data.

## Task 3C — Observability MCP tools

Added observability MCP tools for log search and trace lookup to agent config.

## Task 4A — Multi-step investigation

Agent chains log search, trace ID extraction, trace fetch, and summary into a single response.

## Task 4B — Proactive health check

Configured cron job that sends periodic health check messages through the agent.

## Task 4C — Bug fix and recovery

Found unhandled_exception_handler bug in backend/app/main.py via agent logs investigation.
The function signature was missing the `request` parameter — FastAPI exception handlers require (request, exc).
Fixed by adding `request: Request` as the first parameter. After redeploy, no more 500 errors on unhandled exceptions.
