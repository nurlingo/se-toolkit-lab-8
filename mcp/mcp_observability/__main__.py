"""Observability MCP server — queries VictoriaLogs and VictoriaTraces."""

import json
import os
import urllib.request
from mcp.server.fastmcp import FastMCP

VICTORIALOGS_URL = os.environ.get("VICTORIALOGS_URL", "http://localhost:42010")
VICTORIATRACES_URL = os.environ.get("VICTORIATRACES_URL", "http://localhost:42011")

mcp = FastMCP("observability")


@mcp.tool()
def logs_search(query: str = "*", limit: int = 10, time_window_minutes: int = 60) -> str:
    """Search backend logs in VictoriaLogs using LogsQL syntax."""
    url = f"{VICTORIALOGS_URL}/select/logsql/query?query={urllib.parse.quote(query)}&limit={limit}&start=-{time_window_minutes}m"
    try:
        resp = urllib.request.urlopen(url, timeout=10).read().decode()
        lines = [l for l in resp.strip().split("\n") if l]
        results = []
        for line in lines[:limit]:
            try:
                entry = json.loads(line)
                results.append({
                    "time": entry.get("_time", ""),
                    "message": entry.get("_msg", ""),
                    "level": entry.get("severity", entry.get("level", "")),
                    "trace_id": entry.get("otelTraceID", ""),
                })
            except json.JSONDecodeError:
                results.append({"raw": line[:200]})
        return json.dumps(results, indent=2) if results else "No logs found for the given query."
    except Exception as e:
        return f"Error querying logs: {e}"


@mcp.tool()
def logs_error_count(time_window_minutes: int = 60) -> str:
    """Count error-level log entries in the last N minutes."""
    url = f"{VICTORIALOGS_URL}/select/logsql/query?query=severity:ERROR OR severity:error OR status:5*&limit=100&start=-{time_window_minutes}m"
    try:
        resp = urllib.request.urlopen(url, timeout=10).read().decode()
        lines = [l for l in resp.strip().split("\n") if l]
        return json.dumps({"error_count": len(lines), "time_window_minutes": time_window_minutes})
    except Exception as e:
        return f"Error querying logs: {e}"


@mcp.tool()
def traces_list(service: str = "Learning Management Service", limit: int = 5, time_window_minutes: int = 60) -> str:
    """List recent traces from VictoriaTraces for a service."""
    url = f"{VICTORIATRACES_URL}/select/jaeger/api/traces?service={urllib.parse.quote(service)}&limit={limit}&lookback={time_window_minutes}m"
    try:
        resp = json.loads(urllib.request.urlopen(url, timeout=10).read().decode())
        traces = resp.get("data", [])
        results = []
        for t in traces:
            spans = t.get("spans", [])
            if spans:
                root = spans[0]
                results.append({
                    "trace_id": root.get("traceID", ""),
                    "operation": root.get("operationName", ""),
                    "duration_us": root.get("duration", 0),
                    "span_count": len(spans),
                })
        return json.dumps(results, indent=2) if results else "No traces found."
    except Exception as e:
        return f"Error querying traces: {e}"


@mcp.tool()
def traces_get(trace_id: str) -> str:
    """Fetch a specific trace by ID with all its spans."""
    url = f"{VICTORIATRACES_URL}/select/jaeger/api/traces/{trace_id}"
    try:
        resp = json.loads(urllib.request.urlopen(url, timeout=10).read().decode())
        traces = resp.get("data", [])
        if not traces:
            return f"Trace {trace_id} not found."
        spans = traces[0].get("spans", [])
        results = []
        for s in spans:
            results.append({
                "operation": s.get("operationName", ""),
                "duration_us": s.get("duration", 0),
                "tags": {t["key"]: t["value"] for t in s.get("tags", []) if t["key"] in ("http.method", "http.status_code", "http.url", "error")},
            })
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error fetching trace: {e}"


import urllib.parse  # noqa: E402 (needed for url encoding above)

if __name__ == "__main__":
    mcp.run(transport="stdio")
