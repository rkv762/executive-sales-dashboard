"""Generate synthetic business sales data (200 rows) as CSV."""

from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent / "sales_data.csv"
N_ROWS = 200
SEED = 42


def generate_sales_data(n_rows: int = N_ROWS, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    regions = ["North", "South", "East", "West", "Central"]
    products = [
        "Analytics Suite",
        "Cloud Storage",
        "CRM Pro",
        "Data Pipeline",
        "Security Shield",
        "BI Insights",
    ]
    salespeople = [
        "Aisha Khan",
        "James Chen",
        "Priya Sharma",
        "Marcus Lee",
        "Elena Rossi",
        "Omar Hassan",
        "Sophia Patel",
        "Daniel Kim",
    ]
    segments = ["Enterprise", "Mid-Market", "SMB", "Startup"]

    # Weighted product pricing (unit price bands)
    product_price = {
        "Analytics Suite": (180, 320),
        "Cloud Storage": (40, 90),
        "CRM Pro": (120, 220),
        "Data Pipeline": (200, 400),
        "Security Shield": (150, 280),
        "BI Insights": (90, 180),
    }
    segment_margin = {
        "Enterprise": (0.28, 0.42),
        "Mid-Market": (0.22, 0.35),
        "SMB": (0.15, 0.28),
        "Startup": (0.10, 0.22),
    }

    start = pd.Timestamp("2024-01-01")
    end = pd.Timestamp("2025-09-30")
    day_span = (end - start).days

    dates = [start + pd.Timedelta(days=int(d)) for d in rng.integers(0, day_span + 1, n_rows)]
    region = rng.choice(regions, n_rows)
    product = rng.choice(products, n_rows)
    salesperson = rng.choice(salespeople, n_rows)
    segment = rng.choice(segments, n_rows, p=[0.30, 0.30, 0.25, 0.15])

    units = rng.integers(1, 45, n_rows)
    revenue = np.empty(n_rows, dtype=float)
    profit = np.empty(n_rows, dtype=float)
    ratings = np.empty(n_rows, dtype=float)

    for i in range(n_rows):
        lo, hi = product_price[product[i]]
        unit_price = float(rng.uniform(lo, hi))
        # Slight regional uplift
        if region[i] in ("North", "West"):
            unit_price *= 1.08
        elif region[i] == "South":
            unit_price *= 0.96

        rev = units[i] * unit_price
        m_lo, m_hi = segment_margin[segment[i]]
        margin = float(rng.uniform(m_lo, m_hi))
        # Occasional loss-making deals
        if rng.random() < 0.04:
            margin = float(rng.uniform(-0.08, 0.05))

        revenue[i] = round(rev, 2)
        profit[i] = round(rev * margin, 2)
        # Higher ratings tend to correlate with profitable deals
        base = 3.2 + margin * 3.5 + rng.normal(0, 0.35)
        ratings[i] = float(np.clip(round(base, 1), 1.0, 5.0))

    df = pd.DataFrame(
        {
            "Date": pd.to_datetime(dates).strftime("%Y-%m-%d"),
            "Region": region,
            "Product": product,
            "Salesperson": salesperson,
            "Customer Segment": segment,
            "Units Sold": units,
            "Revenue": revenue,
            "Profit": profit,
            "Customer Rating": ratings,
        }
    ).sort_values("Date").reset_index(drop=True)

    return df


def main() -> None:
    df = generate_sales_data()
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(df)} rows to {OUTPUT_PATH}")
    print(df.head(3).to_string(index=False))
    print("...")
    print(df.tail(2).to_string(index=False))


if __name__ == "__main__":
    main()
