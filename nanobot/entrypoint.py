"""Resolve environment variables into config.json and start nanobot gateway."""
import json, os

def main():
    with open("./config.json") as f:
        config = json.load(f)

    config["providers"]["custom"]["apiKey"] = os.environ.get("LLM_API_KEY", os.environ.get("NANOBOT_LLM_API_KEY", ""))
    config["providers"]["custom"]["apiBase"] = os.environ.get("LLM_API_BASE_URL", os.environ.get("NANOBOT_LLM_BASE_URL", ""))
    config["gateway"]["host"] = os.environ.get("NANOBOT_GATEWAY_HOST", "0.0.0.0")
    config["gateway"]["port"] = int(os.environ.get("NANOBOT_GATEWAY_PORT", "18790"))

    config.setdefault("channels", {})
    config["channels"]["webchat"] = {
        "enabled": True,
        "host": os.environ.get("NANOBOT_WEBCHAT_HOST", "0.0.0.0"),
        "port": int(os.environ.get("NANOBOT_WEBCHAT_PORT", "8765")),
        "accessKey": os.environ.get("NANOBOT_ACCESS_KEY", ""),
        "allowFrom": ["*"]
    }

    mcp = config.get("tools", {}).get("mcpServers", {})
    if "lms" in mcp:
        env = mcp["lms"].setdefault("env", {})
        env["NANOBOT_LMS_BACKEND_URL"] = os.environ.get("NANOBOT_LMS_BACKEND_URL", "http://backend:8000")
        env["NANOBOT_LMS_API_KEY"] = os.environ.get("NANOBOT_LMS_API_KEY", "")

    # MCP tools — Observability (VictoriaLogs + VictoriaTraces)
    if "observability" in mcp:
        env = mcp["observability"].setdefault("env", {})
        env["VICTORIALOGS_URL"] = os.environ.get("VICTORIALOGS_URL", "http://victorialogs:9428")
        env["VICTORIATRACES_URL"] = os.environ.get("VICTORIATRACES_URL", "http://victoriatraces:10428")

    with open("./config.resolved.json", "w") as f:
        json.dump(config, f, indent=2)

    os.execvp("nanobot", ["nanobot", "gateway", "--config", "./config.resolved.json", "--workspace", "./workspace"])

if __name__ == "__main__":
    main()
