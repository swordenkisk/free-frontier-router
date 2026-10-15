# Free Frontier Router

A lightweight command-line assistant that sends prompts to OpenRouter's
`openrouter/free` model router. The router selects from available free models;
it does not guarantee a particular model, quality level, or uninterrupted
availability.

## Features

- Simple command-line interface.
- Configurable model, system prompt, temperature, and response length.
- Bounded retries for network errors, rate limits, and temporary server errors.
- API key loaded from environment configuration.
- No web server or database required.

## Requirements

- Python 3.11 or newer.
- An OpenRouter API key.

## Setup

```bash
git clone https://github.com/swordenkisk/free-frontier-router.git
cd free-frontier-router
chmod +x scripts/setup.sh
./scripts/setup.sh

Open .env and set OPENROUTER_API_KEY:

dotenv


OPENROUTER\_API\_KEY=your\_key\_here
OPENROUTER\_MODEL=openrouter/free
Keep .env out of version control. It is excluded by .gitignore.

Usage
Activate the virtual environment:

bash


source .venv/bin/activate
Ask a question:

bash


free-frontier "Explain how a hash table works."
Set options for a request:

bash


free-frontier "Review this function for edge cases." \\
  --system "You are a careful senior software engineer." \\
  --max-tokens 1200 \\
  --temperature 0.2
Use a specific model supported by your OpenRouter account:

bash


free-frontier "Summarize this idea." --model "provider/model-name"
To change the default model, edit OPENROUTER_MODEL in .env.

Tests
Install pytest and run:

bash


python -m pip install pytest
pytest
Cost and availability
The project defaults to OpenRouter's free-model router. Free inference is
subject to provider availability, rate limits, and account or platform rules.
The router may select different models across requests. Check current model
pricing and terms before relying on a particular model or deploying this
project for production workloads.

Project layout
src/free_frontier/cli.py: command-line arguments and application entry point.
src/free_frontier/client.py: API request, validation, and retry logic.
scripts/setup.sh: creates the virtual environment and installs the package.
.env.example: documents supported environment variables.