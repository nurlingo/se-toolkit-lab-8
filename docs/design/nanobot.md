# Nanobot architecture

> System-level context (container diagram, design decisions): [architecture.md](architecture.md)

This directory contains the nanobot gateway deployment for the LMS — an AI assistant that connects to chat channels and answers questions using LLM reasoning and LMS backend data.

## Upstream dependency

The framework comes from the `nanobot-ai` PyPI package, included as a git submodule at `packages/nanobot-ai/` for local development. Customization is done through the **channel plugin** system (webchat) and **MCP tool servers** (LMS API).

## Directory layout

```
nanobot/
├── packages/
│   └── nanobot-ai/          # Git submodule — nanobot-ai framework (editable)
├── nanobot_webchat/         # WebSocket channel plugin for chat clients
│   └── __init__.py          # WebChatChannel (BaseChannel subclass)
├── workspace/
│   └── skills/lms/SKILL.md  # Teaches the nanobot agent how to use the mcp_lms_* tools
├── config.json              # Gateway config (webchat channel + LMS MCP server)
├── entrypoint.py            # Injects runtime env vars into MCP configs, then execs gateway
├── pyproject.toml           # Dependencies + entry point registration
└── Dockerfile               # Multi-stage build

mcp/                         # Top-level MCP package (separate workspace member)
├── mcp_lms/                 # LMS backend — client + MCP tools
│   ├── __init__.py          # Re-exports from client and server
│   ├── client.py            # HTTP client, models, formatters
│   ├── server.py            # MCP tool definitions + handlers
│   └── __main__.py          # Entry point for `python -m mcp_lms`
└── pyproject.toml           # Package definition (lms-mcp)
```

## How clients connect

Both the Flutter web app and the Telegram bot connect to the **same nanobot instance** over WebSocket. The nanobot gateway exposes a single webchat channel on the port configured by `NANOBOT_WEBCHAT_CONTAINER_PORT` (default 8765).

```
Flutter app        →  WebSocket (ws://nanobot:<NANOBOT_WEBCHAT_CONTAINER_PORT>)  →  nanobot agent
Telegram bot       →  WebSocket (ws://nanobot:<NANOBOT_WEBCHAT_CONTAINER_PORT>)  →  nanobot agent
```

The Telegram bot (`client-telegram-bot/`) is a standalone aiogram service. It handles slash commands directly via the LMS backend API and forwards free-text messages to nanobot over WebSocket.

## Docker services

| Service               | Image source            | Purpose                                              |
| --------------------- | ----------------------- | ---------------------------------------------------- |
| `nanobot`             | `./nanobot`             | AI agent gateway with webchat WebSocket              |
| `client-telegram-bot` | `./client-telegram-bot` | Telegram bot — slash commands + WebSocket forwarding |

Caddy reverse-proxies the nanobot webchat channel: `/ws/chat` → `NANOBOT_WEBCHAT_CONTAINER_PORT`.

## WebSocket protocol

Clients connect to `ws://nanobot:<NANOBOT_WEBCHAT_CONTAINER_PORT>` and exchange JSON messages:

- **Send**: `{"content": "user message"}`
- **Receive**: `{"content": "agent response"}`

Each WebSocket connection gets its own chat session (UUID-based). The agent processes the message, may call tools (mcp_lms_*, read_file), and returns a single response.

## Message flow

### Free text (agent-routed)

```
User sends text in Telegram
  → aiogram receives via long polling
  → bot opens WebSocket to nanobot (NANOBOT_WS_URL)
  → sends {"content": text}
  → nanobot agent reasons with LLM, may call tools
  → agent produces response
  → bot receives {"content": response} over WebSocket
  → bot.send_message(chat_id, response)
```

### Slash commands (direct, no LLM)

```
User sends /scores lab-04
  → aiogram Command("scores") handler fires
  → handler calls LMSClient.get_pass_rates("lab-04") via httpx
  → handler formats result and calls message.answer(text)
```

No agent involvement. Sub-second response. Commands: `/start`, `/help`, `/health`, `/labs`, `/scores <lab>`.

## Environment variables

### nanobot service

| Variable                              | Purpose                                            |
| ------------------------------------- | -------------------------------------------------- |
| `NANOBOT_LMS_BACKEND_URL`             | Backend URL forwarded to the LMS MCP server        |
| `NANOBOT_PROVIDERS__CUSTOM__API_KEY`  | LLM API key                                        |
| `NANOBOT_PROVIDERS__CUSTOM__API_BASE` | LLM API base URL                                   |
| `NANOBOT_GATEWAY_CONTAINER_ADDRESS`   | Gateway bind address (default `0.0.0.0`)           |
| `NANOBOT_GATEWAY_CONTAINER_PORT`      | Gateway HTTP port (default `18790`)                |
| `NANOBOT_WEBCHAT_CONTAINER_ADDRESS`   | WebChat WebSocket bind address (default `0.0.0.0`) |
| `NANOBOT_WEBCHAT_CONTAINER_PORT`      | WebChat WebSocket port (default `8765`)            |

### client-telegram-bot service

| Variable           | Purpose                                     |
| ------------------ | ------------------------------------------- |
| `BOT_TOKEN`        | Telegram bot token                          |
| `LMS_API_KEY`      | Backend auth for direct slash commands      |
| `LMS_API_BASE_URL` | Backend URL for direct slash commands       |
| `NANOBOT_WS_URL`   | Nanobot WebSocket URL                       |

## Debugging checklist

1. **Bot not receiving messages**: Check `docker compose logs client-telegram-bot`. Look for `Starting bot...`. If missing, the token is wrong or aiogram failed to import.

2. **`TelegramConflictError`**: Two processes are polling the same bot token. Stop orphan containers with the same token.

3. **Free text returns "Could not reach the AI agent"**: The nanobot service is down or unreachable. Check `docker compose logs nanobot` and verify the webchat channel started on the expected port (`NANOBOT_WEBCHAT_CONTAINER_PORT`).

4. **Slash commands return "LMS client not configured"**: `LMS_API_BASE_URL` or `LMS_API_KEY` env vars are missing from the client-telegram-bot service.

5. **Slow responses to free text**: The nanobot agent runs tool calls (mcp_lms_*, read_file) before answering. This is normal — the agent may take 10-60s for complex queries. Slash commands bypass this entirely.

6. **`setuptools` build error ("Multiple top-level packages")**: The `[tool.setuptools.packages.find]` section in each `pyproject.toml` must explicitly include its packages — `nanobot_webchat` in `nanobot/pyproject.toml`, `mcp_lms` in `mcp/pyproject.toml`.
