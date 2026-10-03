"""
Executive Business Dashboard — Streamlit
Interactive KPIs and charts that update with sidebar filters.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from generate_data import generate_sales_data

DATA_PATH = Path(__file__).parent / "sales_data.csv"

# ---------------------------------------------------------------------------
# Theme / styling
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Executive Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    /* Reduce default top padding for a tighter executive layout */
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* KPI metric cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #0f2744 0%, #163a5f 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1rem 1.15rem;
        box-shadow: 0 8px 24px rgba(8, 20, 40, 0.25);
    }
    div[data-testid="stMetric"] label {
        color: #9fb4cc !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #f5f8fc !important;
        font-size: 1.65rem !important;
        font-weight: 650 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #a8c5e2 !important;
    }

    /* Sidebar polish */
    section[data-testid="stSidebar"] {
        background: #0b1a2b;
    }
    section[data-testid="stSidebar"] * {
        color: #d7e3ef;
    }

    h1, h2, h3 { letter-spacing: -0.01em; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, Segoe UI, sans-serif", color="#1f2a37", size=12),
    margin=dict(l=40, r=20, t=50, b=40),
    hoverlabel=dict(bgcolor="#0f2744", font_size=12, font_color="#ffffff"),
)

COLOR_SEQUENCE = ["#1f6feb", "#2ea44f", "#d97706", "#8250df", "#cf222e", "#0969da"]


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    """Load CSV if present; otherwise generate and persist synthetic data."""
    if not DATA_PATH.exists():
        df = generate_sales_data()
        df.to_csv(DATA_PATH, index=False)
    else:
        df = pd.read_csv(DATA_PATH)

    df["Date"] = pd.to_datetime(df["Date"])
    return df


def format_currency(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.0f}"


# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
df = load_data()

st.sidebar.markdown("## Filters")
st.sidebar.caption("All KPIs and charts update instantly.")

min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

regions = sorted(df["Region"].unique())
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)

products = sorted(df["Product"].unique())
selected_products = st.sidebar.multiselect("Product", products, default=products)

segments = sorted(df["Customer Segment"].unique())
selected_segments = st.sidebar.multiselect(
    "Customer Segment", segments, default=segments
)

salespeople = sorted(df["Salesperson"].unique())
selected_salespeople = st.sidebar.multiselect(
    "Salesperson", salespeople, default=salespeople
)

st.sidebar.divider()
if st.sidebar.button("Reset filters", use_container_width=True):
    st.cache_data.clear()
    st.rerun()


# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
def apply_filters(data: pd.DataFrame) -> pd.DataFrame:
    filtered = data.copy()

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered = filtered[(filtered["Date"] >= start) & (filtered["Date"] <= end)]
    elif isinstance(date_range, (list, tuple)) and len(date_range) == 1:
        start = pd.to_datetime(date_range[0])
        filtered = filtered[filtered["Date"] >= start]

    if selected_regions:
        filtered = filtered[filtered["Region"].isin(selected_regions)]
    else:
        return filtered.iloc[0:0]

    if selected_products:
        filtered = filtered[filtered["Product"].isin(selected_products)]
    else:
        return filtered.iloc[0:0]

    if selected_segments:
        filtered = filtered[filtered["Customer Segment"].isin(selected_segments)]
    else:
        return filtered.iloc[0:0]

    if selected_salespeople:
        filtered = filtered[filtered["Salesperson"].isin(selected_salespeople)]
    else:
        return filtered.iloc[0:0]

    return filtered


filtered_df = apply_filters(df)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("Executive Sales Dashboard")
st.caption(
    f"Synthetic sales performance · {len(filtered_df):,} of {len(df):,} records shown"
)


# ---------------------------------------------------------------------------
# KPI cards
# ---------------------------------------------------------------------------
total_revenue = float(filtered_df["Revenue"].sum()) if not filtered_df.empty else 0.0
total_profit = float(filtered_df["Profit"].sum()) if not filtered_df.empty else 0.0
total_units = int(filtered_df["Units Sold"].sum()) if not filtered_df.empty else 0
avg_rating = (
    float(filtered_df["Customer Rating"].mean()) if not filtered_df.empty else 0.0
)
margin_pct = (total_profit / total_revenue * 100) if total_revenue else 0.0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Revenue", format_currency(total_revenue))
k2.metric("Total Profit", format_currency(total_profit), f"{margin_pct:.1f}% margin")
k3.metric("Units Sold", f"{total_units:,}")
k4.metric("Avg Customer Rating", f"{avg_rating:.2f} / 5.0")

st.divider()


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
if filtered_df.empty:
    st.warning("No data matches the current filters. Adjust filters in the sidebar.")
    st.stop()

# Row 1: Revenue trend + Revenue by region
c1, c2 = st.columns(2)

with c1:
    st.subheader("Revenue Trend")
    trend = (
        filtered_df.set_index("Date")
        .resample("ME")[["Revenue", "Profit"]]
        .sum()
        .reset_index()
    )
    trend["Month"] = trend["Date"].dt.strftime("%b %Y")
    fig_trend = px.line(
        trend,
        x="Date",
        y="Revenue",
        markers=True,
        title=None,
    )
    fig_trend.update_traces(line=dict(color="#1f6feb", width=3), marker=dict(size=7))
    fig_trend.update_layout(
        **CHART_LAYOUT,
        xaxis_title="",
        yaxis_title="Revenue ($)",
        yaxis_tickprefix="$",
        hovermode="x unified",
    )
    # Add profit as secondary visual via area under revenue
    fig_trend.add_scatter(
        x=trend["Date"],
        y=trend["Profit"],
        mode="lines",
        name="Profit",
        line=dict(color="#2ea44f", width=2, dash="dot"),
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with c2:
    st.subheader("Revenue by Region")
    by_region = (
        filtered_df.groupby("Region", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=True)
    )
    fig_region = px.bar(
        by_region,
        x="Revenue",
        y="Region",
        orientation="h",
        text="Revenue",
        color="Revenue",
        color_continuous_scale=["#dbeafe", "#1f6feb"],
    )
    fig_region.update_traces(
        texttemplate="$%{text:,.0f}",
        textposition="outside",
        showlegend=False,
    )
    fig_region.update_layout(
        **{**CHART_LAYOUT, "margin": dict(l=40, r=60, t=30, b=40)},
        coloraxis_showscale=False,
        xaxis_title="Revenue ($)",
        yaxis_title="",
    )
    st.plotly_chart(fig_region, use_container_width=True)

# Row 2: Product performance + Profit by segment
c3, c4 = st.columns(2)

with c3:
    st.subheader("Product Performance")
    by_product = (
        filtered_df.groupby("Product", as_index=False)
        .agg(Revenue=("Revenue", "sum"), Units=("Units Sold", "sum"))
        .sort_values("Revenue", ascending=False)
    )
    fig_product = px.bar(
        by_product,
        x="Product",
        y="Revenue",
        color="Product",
        color_discrete_sequence=COLOR_SEQUENCE,
        text="Revenue",
        hover_data={"Units": True, "Revenue": ":$,.0f"},
    )
    fig_product.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig_product.update_layout(
        **{**CHART_LAYOUT, "margin": dict(l=40, r=20, t=30, b=80)},
        showlegend=False,
        xaxis_title="",
        yaxis_title="Revenue ($)",
        yaxis_tickprefix="$",
    )
    st.plotly_chart(fig_product, use_container_width=True)

with c4:
    st.subheader("Profit by Customer Segment")
    by_segment = (
        filtered_df.groupby("Customer Segment", as_index=False)["Profit"]
        .sum()
        .sort_values("Profit", ascending=False)
    )
    fig_segment = px.pie(
        by_segment,
        names="Customer Segment",
        values="Profit",
        hole=0.55,
        color="Customer Segment",
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig_segment.update_traces(
        textposition="outside",
        textinfo="label+percent",
        hovertemplate="%{label}<br>Profit: $%{value:,.0f}<extra></extra>",
    )
    fig_segment.update_layout(
        **CHART_LAYOUT,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, x=0.5, xanchor="center"),
        annotations=[
            dict(
                text=format_currency(total_profit),
                x=0.5,
                y=0.5,
                font_size=16,
                showarrow=False,
                font_color="#1f2a37",
            )
        ],
    )
    st.plotly_chart(fig_segment, use_container_width=True)


# ---------------------------------------------------------------------------
# Detail table
# ---------------------------------------------------------------------------
with st.expander("View filtered transaction detail", expanded=False):
    display = filtered_df.sort_values("Date", ascending=False).copy()
    display["Date"] = display["Date"].dt.strftime("%Y-%m-%d")
    display["Revenue"] = display["Revenue"].map(lambda x: f"${x:,.2f}")
    display["Profit"] = display["Profit"].map(lambda x: f"${x:,.2f}")
    st.dataframe(display, use_container_width=True, hide_index=True)
