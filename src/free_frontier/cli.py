"""Command-line interface for Free Frontier Router."""

from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

from free_frontier.client import (
    OpenRouterClient,
    OpenRouterError,
    client_from_environment,
)


DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful assistant. Be accurate, clear, and concise. "
    "If you are unsure, say so."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="free-frontier",
        description="Ask a question using an OpenRouter model.",
    )
    parser.add_argument("prompt", help="The question or instruction to send.")
    parser.add_argument(
        "--system",
        default=DEFAULT_SYSTEM_PROMPT,
        help="System instruction for the assistant.",
    )
    parser.add_argument(
        "--model",
        help="Override OPENROUTER_MODEL for this request.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=1024,
        help="Maximum response tokens (default: 1024).",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature from 0 to 2 (default: 0.7).",
    )
    return parser


def main() -> int:
    load_dotenv()
    args = build_parser().parse_args()

    try:
        client = client_from_environment()
        if args.model:
            client = OpenRouterClient(
                api_key=os.environ["OPENROUTER_API_KEY"],
                model=args.model,
                timeout=client.timeout,
                site_url=os.getenv("OPENROUTER_SITE_URL") or None,
                app_name=os.getenv(
                    "OPENROUTER_APP_NAME",
                    "Free Frontier Router",
                ),
            )

        answer = client.chat(
            messages=[
                {"role": "system", "content": args.system},
                {"role": "user", "content": args.prompt},
            ],
            max_tokens=args.max_tokens,
            temperature=args.temperature,
        )
    except (ValueError, OpenRouterError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
