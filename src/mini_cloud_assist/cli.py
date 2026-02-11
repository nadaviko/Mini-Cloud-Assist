from __future__ import annotations
import asyncio
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from .telemetry import sample_telemetry
from .context_builder import build_context
from .llm import get_llm
from .reasoning import answer_question


console = Console()


def main():
    load_dotenv()
    import argparse

    parser = argparse.ArgumentParser(prog="cloud-assist", description="Cloud Assist Mini (Incident Assistant)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    ask = sub.add_parser("ask", help="Ask a question about an incident")
    ask.add_argument("question", type=str)
    ask.add_argument("--service", type=str, default="checkout")
    ask.add_argument("--show-context", action="store_true")

    args = parser.parse_args()

    if args.cmd == "ask":
        asyncio.run(_run_ask(args.question, args.service, args.show_context))


async def _run_ask(question: str, service: str, show_context: bool):
    telemetry = sample_telemetry()
    ctx = build_context(telemetry, service=service)
    llm = get_llm()

    ans = await answer_question(llm, question, ctx)

    if show_context:
        console.print(Panel(ctx.snapshot, title="Context Snapshot", expand=False))

    console.print(Panel(ans.answer_text, title=f"Answer (confidence: {ans.confidence_hint})", expand=False))
    if ans.unknowns:
        console.print(Panel("\n".join(f"- {u}" for u in ans.unknowns), title="Unknowns", expand=False))
