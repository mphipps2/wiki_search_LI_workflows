from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
import logging

def instrument():
    """Setup OpenTelemetry instrumentation with Phoenix."""
    logging.info("Initializing OpenTelemetry instrumentation with Phoenix.")

    tracer_provider = trace_sdk.TracerProvider()
    span_exporter = OTLPSpanExporter("http://phoenix:6006/v1/traces")
    span_processor = SimpleSpanProcessor(span_exporter)
    tracer_provider.add_span_processor(span_processor)
    trace_api.set_tracer_provider(tracer_provider)
    LlamaIndexInstrumentor().instrument()
    logging.info("Instrumentation complete.")
