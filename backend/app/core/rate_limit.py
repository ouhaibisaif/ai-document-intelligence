from collections import defaultdict, deque
from time import monotonic

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int) -> None:
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        self.clients: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        client_host = request.client.host if request.client else "unknown"
        now = monotonic()
        hits = self.clients[client_host]

        while hits and now - hits[0] > self.window_seconds:
            hits.popleft()

        if len(hits) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down."},
            )

        hits.append(now)
        return await call_next(request)
