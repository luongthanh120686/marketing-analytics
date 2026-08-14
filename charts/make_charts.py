"""
Phase 3 — turn SQL results into charts (PNG) for the README / dashboard.
Reads straight from Postgres and saves 3 charts into charts/.
"""
import warnings
warnings.filterwarnings("ignore")      # tắt cảnh báo read_sql cho gọn

import matplotlib
matplotlib.use("Agg")                  # headless: chỉ LƯU file, không mở cửa sổ
import matplotlib.pyplot as plt
import pandas as pd
import psycopg
from pathlib import Path

DSN = "postgresql://postgres:cc_pass@localhost:5432/marketing"
OUT = Path(__file__).parent


def main():
    with psycopg.connect(DSN) as conn:
        roas = pd.read_sql("""
            SELECT c.channel, ROUND(SUM(d.revenue)/SUM(d.spend),2) AS roas
            FROM daily_performance d JOIN campaigns c ON c.campaign_id=d.campaign_id
            GROUP BY c.channel ORDER BY roas DESC
        """, conn)
        trend = pd.read_sql("""
            SELECT DATE_TRUNC('month',date)::date AS month,
                   ROUND(SUM(revenue)/SUM(spend),2) AS roas
            FROM daily_performance GROUP BY 1 ORDER BY 1
        """, conn)
        topics = pd.read_sql("""
            SELECT topic, COUNT(*) FILTER (WHERE sentiment='negative') AS complaints
            FROM review_labels GROUP BY topic ORDER BY complaints DESC
        """, conn)

    # Chart 1 — ROAS by channel (green = profitable, red = losing)
    plt.figure(figsize=(7, 4))
    colors = ["#2e7d32" if v >= 1 else "#c62828" for v in roas["roas"]]
    plt.bar(roas["channel"], roas["roas"], color=colors)
    plt.axhline(1.0, color="gray", linestyle="--", label="break-even (1.0x)")
    plt.title("ROAS by channel"); plt.ylabel("ROAS (revenue / $1 spend)")
    plt.legend(); plt.tight_layout()
    plt.savefig(OUT / "roas_by_channel.png", dpi=120); plt.close()

    # Chart 2 — monthly ROAS trend
    plt.figure(figsize=(7, 4))
    plt.plot(trend["month"], trend["roas"], marker="o", color="#1565c0")
    plt.axhline(1.0, color="gray", linestyle="--")
    plt.title("Monthly ROAS trend"); plt.ylabel("ROAS"); plt.xticks(rotation=45)
    plt.tight_layout(); plt.savefig(OUT / "monthly_trend.png", dpi=120); plt.close()

    # Chart 3 — complaints by topic (AI-labelled)
    plt.figure(figsize=(7, 4))
    plt.bar(topics["topic"], topics["complaints"], color="#ef6c00")
    plt.title("Customer complaints by topic (AI-labelled)")
    plt.ylabel("negative reviews"); plt.tight_layout()
    plt.savefig(OUT / "complaints_by_topic.png", dpi=120); plt.close()

    print("Saved 3 charts to", OUT)


if __name__ == "__main__":
    main()
