import sqlite3
from datetime import datetime
from app.models import get_db

def insert_message(msg):
    conn = get_db()
    try:
        conn.execute("""
        INSERT INTO messages
        (message_id, from_msisdn, to_msisdn, ts, text, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            msg["message_id"],
            msg["from"],
            msg["to"],
            msg["ts"],
            msg.get("text"),
            datetime.utcnow().isoformat() + "Z"
        ))
        conn.commit()
        return "created"
    except sqlite3.IntegrityError:
        return "duplicate"
    finally:
        conn.close()

def list_messages(limit, offset, from_filter, since, q):
    conn = get_db()
    where = []
    params = []

    if from_filter:
        where.append("from_msisdn = ?")
        params.append(from_filter)
    if since:
        where.append("ts >= ?")
        params.append(since)
    if q:
        where.append("LOWER(text) LIKE ?")
        params.append(f"%{q.lower()}%")

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    total = conn.execute(
        f"SELECT COUNT(*) FROM messages {where_sql}",
        params
    ).fetchone()[0]

    rows = conn.execute(
        f"""
        SELECT message_id, from_msisdn as "from", to_msisdn as "to", ts, text
        FROM messages
        {where_sql}
        ORDER BY ts ASC, message_id ASC
        LIMIT ? OFFSET ?
        """,
        params + [limit, offset]
    ).fetchall()

    conn.close()
    return total, [dict(r) for r in rows]

def stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    senders = conn.execute(
        "SELECT COUNT(DISTINCT from_msisdn) FROM messages"
    ).fetchone()[0]

    per_sender = conn.execute("""
        SELECT from_msisdn as "from", COUNT(*) as count
        FROM messages
        GROUP BY from_msisdn
        ORDER BY count DESC
        LIMIT 10
    """).fetchall()

    first_last = conn.execute(
        "SELECT MIN(ts), MAX(ts) FROM messages"
    ).fetchone()

    conn.close()

    return {
        "total_messages": total,
        "senders_count": senders,
        "messages_per_sender": [dict(r) for r in per_sender],
        "first_message_ts": first_last[0],
        "last_message_ts": first_last[1],
    }
