from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from .context_builder import IncidentContext
from .llm.base import LLM


@dataclass(frozen=True)
class AssistAnswer:
    question: str
    service: str
    answer_text: str
    confidence_hint: str
    evidence: List[str]
    safe_next_steps: List[str]
    unknowns: List[str]


def build_prompt(question: str, ctx: IncidentContext) -> str:
    return f"""
You are an SRE incident assistant embedded in a cloud console.

User question:
{question}

Telemetry context (ground truth, do not invent facts beyond this):
{ctx.snapshot}

Return a response with the following sections:
1) Root cause (hypothesis)
2) Confidence (low/medium/high) and why
3) Evidence (bullet points that quote/point to the context)
4) Safe next steps (no auto-execution; recommend checks/actions)
5) What you don't know / what data you'd request
Keep it concise and operational.
""".strip()


def postprocess(answer_text: str, ctx: IncidentContext) -> AssistAnswer:
    # Lightweight extraction hints (kept simple)
    conf = "medium"
    low = answer_text.lower()
    if "confidence" in low and "high" in low:
        conf = "high"
    if "confidence" in low and "low" in low:
        conf = "low"

    evidence = []
    for h in ctx.highlights[:3]:
        evidence.append(h)

    safe_next_steps = [
        "Review recent deploys and correlate with metric inflection.",
        "Inspect DB saturation / dependency health and retry behavior.",
        "Add traces or request slow query stats if missing.",
    ]
    return AssistAnswer(
        question="",
        service=ctx.service,
        answer_text=answer_text.strip(),
        confidence_hint=conf,
        evidence=evidence,
        safe_next_steps=safe_next_steps,
        unknowns=ctx.unknowns,
    )


async def answer_question(llm: LLM, question: str, ctx: IncidentContext) -> AssistAnswer:
    prompt = build_prompt(question, ctx)
    res = await llm.complete(prompt)
    ans = postprocess(res.text, ctx)
    return AssistAnswer(
        question=question,
        service=ctx.service,
        answer_text=ans.answer_text,
        confidence_hint=ans.confidence_hint,
        evidence=ans.evidence,
        safe_next_steps=ans.safe_next_steps,
        unknowns=ans.unknowns,
    )
