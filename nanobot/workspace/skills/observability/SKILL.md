# Observability Skill

You help investigate system health using logs and traces from the LMS backend.

## Tools

- **logs_search(query, limit, time_window_minutes)** — Search VictoriaLogs with LogsQL.
- **logs_error_count(service, time_window_minutes)** — Count errors by severity.
- **traces_list(service, limit, time_window_minutes)** — List recent traces.
- **traces_get(trace_id)** — Fetch a full trace with all spans.

## Multi-step investigation strategy

When the user asks "what went wrong?" or "any errors?":
1. First call logs_search or logs_error_count to find recent errors.
2. Extract trace IDs from the log results (look for otelTraceID fields).
3. Call traces_get with each trace ID to see the full request lifecycle.
4. Summarize findings: which endpoint failed, what error occurred, how long it took.

Always start with logs (they're faster to scan), then drill into traces for details.
When reporting, include specific error messages and timestamps, not just counts.
