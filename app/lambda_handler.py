"""AWS Lambda entry point.

Mangum adapts ASGI apps (FastAPI) to Lambda's event-driven invocation model.
The same ``app.main:app`` instance that uvicorn serves locally is what we
hand to Mangum here - one app, two deployment targets (Render + AWS).

Lambda invokes ``handler(event, context)`` for every request that arrives
through API Gateway. Mangum translates the API Gateway HTTP API v2 event
into an ASGI scope, runs the FastAPI app against it, and translates the
ASGI response back into Lambda's expected JSON envelope.
"""

from mangum import Mangum

from app.main import app

# ``lifespan="off"`` skips FastAPI's startup / shutdown events. Those don't
# map cleanly to Lambda's per-invocation lifecycle (the container can be
# frozen and thawed between invocations), and our app does not need them.
handler = Mangum(app, lifespan="off")
