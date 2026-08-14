"""
Phase 4 — classify each customer review with a local LLM (Ollama qwen2.5).
Reads reviews from Postgres, asks for sentiment + topic as strict JSON, and
stores the result in review_labels. Idempotent: already-labelled reviews are
skipped, so the script is safe to re-run or resume.
"""
import json
import ollama
import psycopg

DSN = "postgresql://postgres:cc_pass@localhost:5432/marketing"
MODEL = "qwen2.5:7b"

PROMPT = """Label this customer product review.
Reply with ONLY JSON: {{"sentiment": "...", "topic": "..."}}
- sentiment: "positive" or "negative"
- topic: exactly one of: shipping, quality, price, support, other

Review: "{text}"
"""


def classify(text: str) -> tuple[str, str]:
    """Ask the LLM for one review's sentiment + topic (temperature 0 = stable)."""
    resp = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT.format(text=text)}],
        format="json",
        options={"temperature": 0},
    )
    data = json.loads(resp["message"]["content"])
    return data["sentiment"].lower(), data["topic"].lower()


def main():
    with psycopg.connect(DSN) as conn:
        rows = conn.execute("""
            SELECT r.review_id, r.review_text
            FROM reviews r
            LEFT JOIN review_labels l ON l.review_id = r.review_id
            WHERE l.review_id IS NULL          -- chỉ review CHƯA phân loại
            ORDER BY r.review_id
        """).fetchall()

        print(f"{len(rows)} reviews to classify...")
        for i, (review_id, text) in enumerate(rows, 1):
            sentiment, topic = classify(text)
            conn.execute(
                "INSERT INTO review_labels (review_id, sentiment, topic) VALUES (%s, %s, %s)",
                (review_id, sentiment, topic),
            )
            if i % 20 == 0:
                conn.commit()
                print(f"  {i}/{len(rows)} labelled")
        conn.commit()
    print("Done.")


if __name__ == "__main__":
    main()
