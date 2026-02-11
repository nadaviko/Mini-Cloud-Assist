from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class LogLine:
    timestamp: str
    level: str
    service: str
    msg: str


@dataclass(frozen=True)
class Telemetry:
    logs: List[LogLine]
    metrics: Dict[str, List[float]]


def sample_telemetry() -> Telemetry:
    # A tiny realistic-ish sample: db CPU spikes + checkout timeout logs + rising latency/errors.
    logs = [
        LogLine("10:01", "ERROR", "checkout", "DB connection timeout"),
        LogLine("10:02", "ERROR", "checkout", "Retry failed"),
        LogLine("10:02", "WARN", "api", "Latency above threshold"),
        LogLine("10:03", "ERROR", "checkout", "DB connection timeout"),
        LogLine("10:04", "INFO", "deploy", "checkout:v2.7 rolled out to 20%"),
    ]
    metrics = {
        "checkout_latency_ms": [120, 130, 145, 420, 480],
        "db_cpu_pct": [40, 45, 48, 92, 95],
        "error_rate_pct": [1.0, 1.1, 1.3, 6.8, 7.1],
        "rps": [210, 220, 215, 240, 245],
    }
    return Telemetry(logs=logs, metrics=metrics)
