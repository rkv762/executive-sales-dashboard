# Executive Sales Dashboard

Interactive Streamlit business dashboard backed by synthetic sales data.

## Quick start

```bash
cd "Cursor demo"
pip install -r requirements.txt
python generate_data.py    # creates sales_data.csv (200 rows)
streamlit run app.py
```

If `sales_data.csv` is missing, the dashboard generates it automatically on first run.

## Data columns

| Column | Description |
|--------|-------------|
| Date | Transaction date |
| Region | North / South / East / West / Central |
| Product | Product line |
| Salesperson | Account owner |
| Customer Segment | Enterprise / Mid-Market / SMB / Startup |
| Units Sold | Units in the deal |
| Revenue | Deal revenue ($) |
| Profit | Deal profit ($) |
| Customer Rating | 1.0–5.0 |

## Dashboard features

- **KPI cards:** Total Revenue, Total Profit, Units Sold, Average Customer Rating
- **Filters:** Date range, Region, Product, Customer Segment, Salesperson
- **Charts:** Revenue trend, Revenue by region, Product performance, Profit by segment
- All metrics and charts refresh when filters change

## Deploy on Streamlit Community Cloud

1. Open [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub and authorize access to `rkv762/executive-sales-dashboard`
3. Click **New app** and set:
   - **Repository:** `rkv762/executive-sales-dashboard`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Click **Deploy**

