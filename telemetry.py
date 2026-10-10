from opentelemetry import trace

from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)

from opentelemetry.sdk.resources import (
    Resource,
    SERVICE_NAME,
)

from opentelemetry.sdk.trace import (
    TracerProvider,
)

from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)


def setup_tracing():

    resource = Resource.create(
        {
            SERVICE_NAME: "backend-ai",
        }
    )

    tracer_provider = TracerProvider(
        resource=resource
    )

    exporter = OTLPSpanExporter(
        endpoint="http://jaeger:4318/v1/traces"
    )

    span_processor = BatchSpanProcessor(
        exporter
    )

    tracer_provider.add_span_processor(
        span_processor
    )

    trace.set_tracer_provider(
        tracer_provider
    )