from cloud_assist_mini.telemetry import sample_telemetry
from cloud_assist_mini.context_builder import build_context

def test_build_context_contains_key_sections():
    t = sample_telemetry()
    ctx = build_context(t, service="checkout")
    assert "Service: checkout" in ctx.snapshot
    assert "Metrics (coarse):" in ctx.snapshot
    assert "Recent log signals:" in ctx.snapshot
