# Gradio Chatbot

A simple chatbot application using Gradio and OpenAI API, deployed to Google Cloud Run.

## Features

- Simple chat interface using Gradio
- OpenAI GPT model selection (GPT-5, GPT-5-mini, GPT-5-nano)
- Adjustable parameters (temperature, max_tokens, top_p)
- Chat history preservation
- Chat reset functionality
- Secure API key management via Google Secret Manager

## Development

### Local Development

```bash
# Install dependencies
uv sync

# Run locally
uv run python app.py

# Code formatting
uv run ruff format

# Linting
uv run ruff check

# Type checking
uv run mypy .

# Run tests
uv run pytest
```

### Environment Variables

- `OPENAI_API_KEY`: OpenAI API key (loaded from Google Secret Manager in production)

## Deployment

This app is deployed to Google Cloud Run via GitHub Actions. See the main project README for deployment instructions.