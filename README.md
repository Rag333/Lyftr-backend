# Lyftr AI – Backend Assignment

This project implements a production-style webhook ingestion service using FastAPI, with HMAC authentication, idempotent message handling, pagination, analytics, structured logging, metrics, and Docker-based deployment.

---

## How to Run

### Prerequisites
- Docker Desktop
- Docker Compose (v2)

### Start the service

export WEBHOOK_SECRET="testsecret"
export DATABASE_URL="sqlite:////data/app.db"

make up

The API will be available at:

http://localhost:8000

### Stop the service

make down

---

## Health Checks

curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready

Expected response:

{"status":"alive"}
{"status":"ready"}

---

## How to Hit Endpoints

### POST /webhook

Receives WhatsApp-like webhook messages.
Messages are processed idempotently.

Headers:
- Content-Type: application/json
- X-Signature: <HMAC-SHA256 signature>

Request Body:
{
  "message_id": "m1",
  "from": "+919876543210",
  "to": "+14155550100",
  "ts": "2025-01-15T10:00:00Z",
  "text": "Hello"
}

Responses:
- 200 {"status":"ok"} → accepted or duplicate
- 401 {"detail":"invalid signature"} → invalid signature
- 422 → validation error

---

### GET /messages

Returns stored messages with pagination and filtering.

Query Parameters:
- limit (default: 50, max: 100)
- offset (default: 0)
- from (sender filter)
- since (timestamp filter)
- q (substring search on text)

Examples:

curl http://localhost:8000/messages
curl "http://localhost:8000/messages?limit=2&offset=0"
curl "http://localhost:8000/messages?from=+919876543210"
curl "http://localhost:8000/messages?q=Hello"

---

### GET /stats

Returns aggregated analytics about stored messages.

curl http://localhost:8000/stats

---

### GET /metrics

Prometheus-style metrics endpoint.

curl http://localhost:8000/metrics

---

## Design Decisions

### HMAC Verification
- Signature is computed as:
  HMAC_SHA256(WEBHOOK_SECRET, raw request body bytes)
- Comparison uses constant-time comparison to prevent timing attacks.
- Invalid or missing signatures return 401 and are not stored.

---

### Idempotency
- Enforced at the database level using message_id as the primary key.
- Duplicate webhook requests return 200 OK without creating new records.

---

### Pagination Contract
- total reflects the total number of records matching filters.
- limit and offset only control pagination.
- Ordering is deterministic:
  ORDER BY ts ASC, message_id ASC

---

### /stats Definition
The /stats endpoint returns:
- total_messages
- senders_count
- messages_per_sender
- first_message_ts
- last_message_ts

When no messages exist, timestamps are returned as null.

---

### Metrics
Exposed in Prometheus text format:
- http_requests_total
- webhook_requests_total{result="ok|duplicate|invalid_signature"}

Used for basic observability and webhook outcome tracking.

---

### Structured Logging
Each request emits a single JSON log entry containing:
- timestamp
- request_id
- method
- path
- status
- latency_ms

Webhook logs additionally include:
- message_id
- duplicate
- result

---

## Technology Stack
- FastAPI
- Python 3.11
- SQLite
- Docker and Docker Compose

---

## Summary

This service:
- Runs entirely via Docker
- Verifies webhook authenticity
- Guarantees idempotent ingestion
- Supports pagination and filtering
- Exposes health checks, metrics, and analytics
- Follows production-oriented backend practices

---

Author: Mahipal Singh

