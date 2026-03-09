from fastapi import FastAPI
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time

request_count = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint"])
request_duration = Histogram("http_request_duration_seconds", "HTTP request duration", ["method", "endpoint"])

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        endpoint = request.url.path
        request_count.labels(method=method, endpoint=endpoint).inc()
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        return response

def setup_metrics(app: FastAPI):
    app.add_middleware(MetricsMiddleware)

    @app.get("/metrics")
    async def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)