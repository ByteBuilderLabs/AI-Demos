import time
from langfuse import get_client, observe
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from dotenv import load_dotenv

load_dotenv()

langfuse = get_client()

exporter = OTLPMetricExporter()
reader = PeriodicExportingMetricReader(exporter, export_interval_millis=5000)
provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)
meter = metrics.get_meter("langgraph-agent")


node_counter = meter.create_counter("agent.node.invocations")
latency_histogram = meter.create_histogram("agent.node.duration_ms")
error_counter = meter.create_counter("agent.node.errors")

def observe_node(node_name: str):
    def decorator(func):
        @observe(name=node_name)
        def wrapper(state):
            start = time.time()
            try:
                result = func(state)
                duration = (time.time() - start) * 1000
                node_counter.add(1, {"node": node_name})
                latency_histogram.record(duration, {"node": node_name})
                return result
            except Exception as e:
                error_counter.add(1, {"node": node_name, "error": type(e).__name__})
                raise
        return wrapper
    return decorator