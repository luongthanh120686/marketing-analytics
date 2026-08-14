"""
Synthetic marketing dataset generator (NOT real data — simulated for a
portfolio analytics project). Deterministic: same seed -> same output, so
every SQL/EDA result is reproducible.

Models a small DTC skincare brand running paid ads on 4 channels in H1 2026:
  - campaigns.csv          one row per ad campaign
  - daily_performance.csv  one row per campaign per active day (spend, clicks, conversions, revenue)
  - reviews.csv            customer reviews in English (feeds the AI layer)

Metrics stay inside realistic ranges per channel (CTR / CVR / CAC / ROAS)
but are simulated. No external dependencies — standard library only.
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 2026
random.seed(SEED)

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# --- period: first half of 2026 (close to "now") ---
START = date(2026, 1, 1)
END = date(2026, 6, 30)

# --- per-channel behaviour profiles (realistic ballparks, simulated) ---
# ctr = click-through rate, cvr = conversion rate, cpc = cost per click (USD).
# Tuned so channels SPREAD: Google is the star, Meta a reliable workhorse,
# TikTok cheap-but-weak, LinkedIn a money pit for a DTC brand (wrong audience).
CHANNELS = {
    "Meta Ads":     {"ctr": 0.015, "cvr": 0.030, "cpc": 0.85, "reach": 1.00},
    "Google Ads":   {"ctr": 0.032, "cvr": 0.070, "cpc": 1.45, "reach": 0.70},
    "TikTok Ads":   {"ctr": 0.012, "cvr": 0.011, "cpc": 0.45, "reach": 1.30},
    "LinkedIn Ads": {"ctr": 0.006, "cvr": 0.016, "cpc": 3.20, "reach": 0.35},
}

# Objective shifts how often a click converts: a conversion-optimised campaign
# sells more per click than an awareness one (which is bought for reach, not
# sales — so judging it by ROAS alone is a trap the analysis should catch).
OBJECTIVE_CVR = {"Conversions": 1.00, "Traffic": 0.65, "Awareness": 0.40}

OBJECTIVES = ["Awareness", "Traffic", "Conversions"]
AOV = 55.0  # average order value in USD

PRODUCTS = ["Vitamin C Serum", "Hydrating Cream", "Sunscreen SPF50",
            "Gentle Cleanser", "Retinol Night Oil"]


def _noise(base, pct):
    """Multiply base by a random factor within +/- pct."""
    return base * (1 + random.uniform(-pct, pct))


def gen_campaigns():
    """8 campaigns with staggered run windows and per-channel budgets."""
    rows = []
    cid = 1
    plan = [
        ("Meta Ads", "Conversions"), ("Meta Ads", "Awareness"),
        ("Google Ads", "Conversions"), ("Google Ads", "Traffic"),
        ("TikTok Ads", "Awareness"), ("TikTok Ads", "Traffic"),
        ("LinkedIn Ads", "Conversions"), ("Meta Ads", "Traffic"),
    ]
    for channel, objective in plan:
        start = START + timedelta(days=random.randint(0, 40))
        length = random.randint(70, 150)
        end = min(start + timedelta(days=length), END)
        daily_budget = random.choice([40, 60, 80, 100, 120, 150])
        rows.append({
            "campaign_id": cid,
            "channel": channel,
            "campaign_name": f"{channel.split()[0]} {objective} {start.strftime('%b')}",
            "objective": objective,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "daily_budget": daily_budget,
        })
        cid += 1
    return rows


def gen_daily(campaigns):
    """One row per campaign per active day, with simulated funnel metrics."""
    rows = []
    for c in campaigns:
        prof = CHANNELS[c["channel"]]
        start = date.fromisoformat(c["start_date"])
        end = date.fromisoformat(c["end_date"])
        day = start
        while day <= end:
            # spend paces around the daily budget
            spend = round(_noise(c["daily_budget"], 0.20), 2)
            clicks = max(0, int(_noise(spend / prof["cpc"], 0.15)))
            impressions = int(clicks / prof["ctr"] * _noise(1, 0.10)) if clicks else 0
            cvr = prof["cvr"] * OBJECTIVE_CVR[c["objective"]]
            # probabilistic rounding: keep the fractional part as a chance of
            # +1, so small daily expectations (e.g. 0.3/day) don't vanish to 0
            # when floored every day — the kept conversions match expectation.
            exp = _noise(clicks * cvr, 0.30)
            conversions = int(exp) + (1 if random.random() < (exp - int(exp)) else 0)
            revenue = round(conversions * _noise(AOV, 0.25), 2)
            rows.append({
                "date": day.isoformat(),
                "campaign_id": c["campaign_id"],
                "impressions": impressions,
                "clicks": clicks,
                "spend": spend,
                "conversions": conversions,
                "revenue": revenue,
            })
            day += timedelta(days=1)
    return rows


# --- review templates by (sentiment, topic) so the AI layer has real signal ---
REVIEW_BANK = {
    "positive": {
        "shipping": ["Arrived two days early, super fast shipping.",
                     "Delivery was quick and the package was intact."],
        "quality":  ["My skin feels amazing after two weeks, great quality.",
                     "Texture is lovely and it actually works."],
        "price":    ["Worth every dollar, does more than pricier brands.",
                     "Great value for the price, will rebuy."],
        "support":  ["Customer support replied in minutes and solved it.",
                     "The team was so helpful when I asked about ingredients."],
    },
    "negative": {
        "shipping": ["Took three weeks to arrive, way too slow.",
                     "Package was damaged and leaking on arrival."],
        "quality":  ["Broke me out badly, the formula feels cheap.",
                     "Stopped working after a week, disappointed."],
        "price":    ["Overpriced for what you get, not worth it.",
                     "Way too expensive compared to similar serums."],
        "support":  ["Emailed support twice and got no reply.",
                     "Support was rude and refused a refund."],
    },
}


def gen_reviews(n=420):
    """Reviews with rating tied to sentiment; topic drives the text."""
    rows = []
    span = (END - START).days
    for rid in range(1, n + 1):
        # ~62% happy customers, ~38% unhappy — a realistic mix
        sentiment = "positive" if random.random() < 0.62 else "negative"
        topic = random.choice(list(REVIEW_BANK[sentiment].keys()))
        text = random.choice(REVIEW_BANK[sentiment][topic])
        rating = random.choice([4, 5, 5]) if sentiment == "positive" else random.choice([1, 2, 2])
        d = START + timedelta(days=random.randint(0, span))
        rows.append({
            "review_id": rid,
            "date": d.isoformat(),
            "product": random.choice(PRODUCTS),
            "rating": rating,
            "review_text": text,
        })
    return rows


def write_csv(name, rows):
    path = DATA_DIR / name
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return path, len(rows)


def main():
    campaigns = gen_campaigns()
    daily = gen_daily(campaigns)
    reviews = gen_reviews()

    for name, rows in [("campaigns.csv", campaigns),
                       ("daily_performance.csv", daily),
                       ("reviews.csv", reviews)]:
        path, n = write_csv(name, rows)
        print(f"  {name:24} {n:>5} rows")

    total_spend = sum(r["spend"] for r in daily)
    total_rev = sum(r["revenue"] for r in daily)
    print(f"\n  period      : {START} -> {END}")
    print(f"  campaigns   : {len(campaigns)} across {len(CHANNELS)} channels")
    print(f"  total spend : ${total_spend:,.0f}")
    print(f"  total revenue: ${total_rev:,.0f}")
    print(f"  blended ROAS: {total_rev / total_spend:.2f}x  (revenue per $1 spent)")
    print("\n  NOTE: simulated data for a portfolio project — not real figures.")


if __name__ == "__main__":
    main()
