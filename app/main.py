from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
import hmac, hashlib
from app.config import WEBHOOK_SECRET
from app.models import init_db
from app.storage import insert_message, list_messages, stats
from app.logging_utils import log_request
from app.metrics import http_requests, webhook_results, render_metrics

app = FastAPI()
app.middleware("http")(log_request)

@app.on_event("startup")
def startup():
    init_db()

class WebhookMessage(BaseModel):
    message_id: str
    from_: str = Field(..., alias="from", pattern=r"^\+\d+$")
    to: str = Field(..., pattern=r"^\+\d+$")
    ts: str
    text: str | None = Field(None, max_length=4096)

def verify_signature(raw, sig):
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        raw,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, sig)

@app.post("/webhook")
async def webhook(request: Request):
    raw = await request.body()
    sig = request.headers.get("X-Signature")

    if not sig or not verify_signature(raw, sig):
        webhook_results["invalid_signature"] += 1
        raise HTTPException(401, "invalid signature")

    payload = await request.json()
    msg = WebhookMessage(**payload)

    result = insert_message({
        "message_id": msg.message_id,
        "from": msg.from_,
        "to": msg.to,
        "ts": msg.ts,
        "text": msg.text
    })

    webhook_results[result] += 1
    return {"status": "ok"}

@app.get("/messages")
def messages(limit: int = 50, offset: int = 0, from_: str | None = None, since: str | None = None, q: str | None = None):
    total, data = list_messages(limit, offset, from_, since, q)
    return {
        "data": data,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.get("/stats")
def stats_endpoint():
    return stats()

@app.get("/health/live")
def live():
    return {"status": "alive"}

@app.get("/health/ready")
def ready():
    return {"status": "ready"}

@app.get("/metrics")
def metrics():
    return render_metrics()
