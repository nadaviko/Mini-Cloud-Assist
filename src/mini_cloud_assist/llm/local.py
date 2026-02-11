from __future__ import annotations
from .base import LLMResult


class LocalHeuristicLLM:
    async def complete(self, prompt: str) -> LLMResult:
        # Very small "reasoner" that mimics an SRE-style output.
        # It looks for common patterns in the prompt.
        p = prompt.lower()
        root = "Insufficient data to determine a likely root cause."
        confidence = "low"
        actions = []

        if "db cpu is critically high" in p or "db cpu" in p and "95" in p:
            root = "Database saturation is likely causing connection timeouts and elevated latency."
            confidence = "high"
            actions = [
                "Check top DB queries / slow query log and recent schema changes.",
                "Scale DB (vertical/horizontal) or add read replicas if applicable.",
                "Reduce retry storm / add backoff and circuit breaking.",
            ]
        elif "deploy" in p and "latency increased" in p:
            root = "A recent deployment may have introduced a performance regression."
            confidence = "medium"
            actions = [
                "Compare latency before/after deploy; canary rollback if correlated.",
                "Inspect recent code paths and DB query changes.",
            ]

        response = "\n".join([
            "Root cause (hypothesis):",
            f"- {root}",
            "",
            "Confidence:",
            f"- {confidence}",
            "",
            "Recommended next actions:",
            *[f"- {a}" for a in actions] if actions else ["- Gather more telemetry (traces, DB metrics, recent changes)."],
            "",
            "What I don't know:",
            "- I cannot confirm without traces, DB query stats, and dependency health.",
        ])
        return LLMResult(text=response, raw={"provider": "local"})
