from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple
from .telemetry import Telemetry, LogLine


@dataclass(frozen=True)
class IncidentContext:
    service: str
    snapshot: str
    highlights: List[str]
    unknowns: List[str]


def _trend(values: List[float]) -> str:
    if len(values) < 2:
        return "unknown"
    return "up" if values[-1] > values[0] else "down" if values[-1] < values[0] else "flat"


def _pct_change(values: List[float]) -> float:
    if len(values) < 2 or values[0] == 0:
        return 0.0
    return (values[-1] - values[0]) / values[0] * 100.0


def _top_log_signals(logs: List[LogLine], service: str, limit: int = 6) -> List[str]:
    # Keep it simple: pick most relevant lines for the target service and infra hints.
    keywords = ("timeout", "failed", "latency", "error", "permission", "quota", "deploy")
    scored: List[Tuple[int, LogLine]] = []
    for line in logs:
        score = 0
        if line.service == service:
            score += 3
        if any(k in line.msg.lower() for k in keywords):
            score += 2
        if line.level in ("ERROR", "WARN"):
            score += 1
        scored.append((score, line))
    scored.sort(key=lambda x: x[0], reverse=True)
    picks = [f"{l.timestamp} {l.level} {l.service}: {l.msg}" for _, l in scored[:limit]]
    return picks


def build_context(telemetry: Telemetry, service: str = "checkout") -> IncidentContext:
    m = telemetry.metrics
    highlights: List[str] = []
    unknowns: List[str] = []

    def describe_metric(name: str, unit: str = "") -> str:
        vals = m.get(name, [])
        if not vals:
            unknowns.append(f"Missing metric: {name}")
            return f"- {name}: missing"
        t = _trend(vals)
        pc = _pct_change(vals)
        return f"- {name}: start={vals[0]:.2f}{unit}, end={vals[-1]:.2f}{unit}, trend={t}, change={pc:.1f}%"

    latency_line = describe_metric("checkout_latency_ms", "ms")
    error_line = describe_metric("error_rate_pct", "%")
    dbcpu_line = describe_metric("db_cpu_pct", "%")
    rps_line = describe_metric("rps")

    # Simple heuristic highlights
    if m.get("db_cpu_pct", [0])[-1] >= 90:
        highlights.append("DB CPU is critically high (>= 90%), suggesting saturation or hot queries.")
    if m.get("error_rate_pct", [0])[-1] >= 5:
        highlights.append("Error rate spiked (>= 5%), likely user-impacting.")
    if m.get("checkout_latency_ms", [0])[-1] >= 300:
        highlights.append("Latency increased sharply (>= 300ms), indicating performance regression or downstream contention.")

    log_signals = _top_log_signals(telemetry.logs, service=service, limit=6)

    snapshot = "\n".join([
        f"Service: {service}",
        "",
        "Metrics (coarse):",
        latency_line,
        error_line,
        dbcpu_line,
        rps_line,
        "",
        "Recent log signals:",
        *[f"- {s}" for s in log_signals],
        "",
        "Key highlights:",
        *[f"- {h}" for h in highlights] if highlights else ["- (none)"],
        "",
        "Unknowns / missing context:",
        *[f"- {u}" for u in unknowns] if unknowns else ["- (none)"],
    ])

    return IncidentContext(service=service, snapshot=snapshot, highlights=highlights, unknowns=unknowns)
