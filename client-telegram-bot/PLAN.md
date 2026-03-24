# SE Toolkit Bot - Implementation Plan

## Overview

This document outlines the implementation plan for building a Telegram bot that lets users interact with the LMS backend through chat. The bot supports slash commands like `/health`, `/labs`, and `/scores`, as well as natural language queries processed by an LLM.

## Architecture

### Handler Architecture (Separation of Concerns)

The bot uses a **testable handler architecture** where command handlers are plain functions that take input and return text. They don't depend on Telegram, so the same function works from:

- `--test` mode (CLI testing without Telegram)
- Unit tests
- The actual Telegram bot

This is called **separation of concerns** — the handler logic is separate from the transport layer (Telegram).

### Project Structure

```
bot/
├── bot.py              # Entry point with --test mode and Telegram startup
├── config.py           # Environment variable loading from .env.docker.secret
├── handlers/
│   ├── __init__.py
│   ├── commands.py     # Slash command handlers (/start, /help, /health, etc.)
│   └── intent_router.py # LLM-based natural language routing
├── services/
│   ├── __init__.py
│   ├── lms_client.py   # LMS backend API client
│   └── llm_client.py   # LLM API client for intent routing
├── pyproject.toml      # Bot dependencies
└── PLAN.md             # This file
```

## Task 1: Plan and Scaffold

**Goal:** Create project structure with testable handler architecture.

**Deliverables:**

- `bot/bot.py` with `--test` mode support
- `bot/handlers/` directory with placeholder handlers
- `bot/config.py` for environment loading
- `client-telegram-bot/pyproject.toml` for dependencies
- `.env.docker.secret` with required variables

**Key Design Decision:** The `--test` flag allows testing handlers without a Telegram connection. This is crucial for rapid development and CI/CD.

## Task 2: Backend Integration

**Goal:** Connect handlers to the real LMS backend.

**Commands to implement:**

1. `/start` — Welcome message with bot name
2. `/help` — List all available commands
3. `/health` — Call backend `/items/`, report up/down status with actual error messages
4. `/labs` — List available labs from backend
5. `/scores <lab>` — Show per-task pass rates

**Error Handling:** When the backend is down, show user-friendly messages that include the actual error (e.g., "connection refused") — not raw tracebacks, not vague messages.

**API Client Pattern:** Use `httpx.AsyncClient` with Bearer token authentication. All URLs and keys come from environment variables.

## Task 3: Intent-Based Natural Language Routing

**Goal:** Allow users to ask questions in plain language.

**Implementation:**

- LLM client that calls Qwen Code API
- Tool definitions for all 9 backend endpoints
- System prompt that teaches the LLM when to use each tool
- Intent router that:
  1. Sends user message to LLM with tool definitions
  2. LLM decides which tool to call
  3. Execute the tool (call backend API)
  4. Send result back to LLM for natural language response

**Key Insight:** The LLM reads tool descriptions to decide which to call. Description quality matters more than prompt engineering. Don't use regex or keyword matching — let the LLM route.

## Task 4: Containerize and Document

**Goal:** Deploy the bot alongside the backend on the VM.

**Deliverables:**

- `bot/Dockerfile` — Container image for the bot
- Update `docker-compose.yml` — Add bot service
- Update `.env.docker.secret` — Add bot environment variables
- README documentation for deployment

**Docker Networking:** Containers use service names, not `localhost`. The bot connects to `http://backend:42002` inside Docker, not `http://localhost:42002`.

## Testing Strategy

1. **Test mode:** `uv run bot.py --test "/command"` for each command
2. **Edge cases:** Missing arguments, unknown commands, non-existent labs
3. **Error handling:** Stop backend, verify friendly error messages
4. **Telegram testing:** Deploy and test in real Telegram

## Git Workflow

For each task:

1. Create issue on GitHub
2. Create branch: `task-N-description`
3. Implement and test
4. Create PR with `Closes #...` in description
5. Partner review
6. Merge

## Deployment Checklist

- [ ] Backend running on VM
- [ ] `.env.docker.secret` has bot credentials (`BOT_TOKEN`, `LLM_API_KEY`)
- [ ] `.env.docker.secret` updated with bot config
- [ ] Bot service added to `docker-compose.yml`
- [ ] `docker compose up -d` starts all services
- [ ] Bot responds in Telegram
