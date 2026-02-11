from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from .telemetry import sample_telemetry
from .context_builder import build_context
from .llm import get_llm
from .reasoning import answer_question

load_dotenv()

app = FastAPI(title="Cloud Assist Mini", version="0.1.0")


class AskRequest(BaseModel):
    question: str
    service: str = "checkout"


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/ask")
async def ask(req: AskRequest):
    telemetry = sample_telemetry()
    ctx = build_context(telemetry, service=req.service)
    llm = get_llm()
    ans = await answer_question(llm, req.question, ctx)
    return {
        "question": ans.question,
        "service": ans.service,
        "confidence_hint": ans.confidence_hint,
        "answer": ans.answer_text,
        "evidence": ans.evidence,
        "safe_next_steps": ans.safe_next_steps,
        "unknowns": ans.unknowns,
        "context_snapshot": ctx.snapshot,
    }
