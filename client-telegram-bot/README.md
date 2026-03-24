# SE Toolkit Bot

Telegram bot for interacting with the LMS backend.

## Quick Start

### 1. Setup environment

All bot variables are set in `.env.docker.secret` (see [wiki/dotenv-docker-secret.md](../wiki/dotenv-docker-secret.md)):

- `BOT_TOKEN` — Telegram bot token from @BotFather
- `LMS_API_KEY` — LMS API key
- `LLM_API_KEY` — Qwen Code API key
- `LLM_API_BASE_URL` — Qwen Code API base URL
- `LLM_API_MODEL` — Model name (e.g., `coder-model`)

### 2. Test mode

Test commands without Telegram:

```bash
uv run bot.py --test "/start"
uv run bot.py --test "/help"
uv run bot.py --test "/health"
uv run bot.py --test "/labs"
uv run bot.py --test "/scores lab-04"
```

### 3. Run the bot

```bash
uv run bot.py
```

## Available Commands

| Command         | Description               |
| --------------- | ------------------------- |
| `/start`        | Welcome message           |
| `/help`         | List all commands         |
| `/health`       | Check backend status      |
| `/labs`         | List available labs       |
| `/scores <lab>` | View pass rates for a lab |

## Natural Language Queries

You can also ask questions in plain language:

- "What labs are available?"
- "Show me the scores for lab-04"
- "Is the backend working?"
- "Who are the top learners in lab-01?"

## Docker Deployment

Add to `.env.docker.secret`:

```bash
BOT_TOKEN=your-telegram-bot-token
LMS_API_BASE_URL=http://backend:8000
LLM_API_KEY=your-qwen-api-key
LLM_API_BASE_URL=http://host.docker.internal:42005/v1
LLM_API_MODEL=coder-model
```

Then run:

```bash
docker compose --env-file .env.docker.secret up -d bot
```

## Architecture

- **Handlers** (`handlers/`) — Command logic, testable without Telegram
- **Services** (`services/`) — API clients for LMS and LLM
- **Entry point** (`bot.py`) — `--test` mode and Telegram startup
