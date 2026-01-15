# Lyftr AI – Backend Assignment

A containerized FastAPI service that ingests WhatsApp-like webhook messages
with idempotency, HMAC verification, observability, and analytics.

---

## How to Run

```bash
export WEBHOOK_SECRET="testsecret"
export DATABASE_URL="sqlite:////data/app.db"

make up
# Lyftr-backend
