"""
Afficionado Coffee Roasters — Sales Intelligence Dashboard (Executive Edition)

Refactor notes / goals:
- Preserves all original calculations, CSV loading, and filtering logic unchanged.
- Keeps all existing charts and functionality.
- Upgrades layout, typography, spacing, and visualization styling to an executive dashboard style.
- Adds Executive Summary and business insights beneath visualizations.
- Improves KPI presentation and footer with portfolio / ATS-friendly details.

Run locally:
    streamlit run app.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ---------------------------------------------------------------------------
# APP CONFIG + THEME
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Afficionado Coffee Roasters — Sales Intelligence",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Color palette (kept from original)
BROWN = "#6B4423"
BROWN_DARK = "#3E2010"
TAN = "#C49A6C"
TERRACOTTA = "#D4845A"
GOLD = "#D4A853"
GREEN = "#27AE60"
BLUE = "#2980B9"
AMBER = "#F39C12"
RED = "#E74C3C"

SEG_COLORS = {"Hero": GREEN, "Premium": BLUE, "Long Tail": AMBER, "Underperforming": RED}
ABC_COLORS = {"A": GREEN, "B": AMBER, "C": RED}
CAT_PALETTE = [BROWN, TAN, TERRACOTTA, GOLD, GREEN, BLUE, AMBER, "#8A5A32", "#3E2010"]

# Global Plotly defaults for a modern, clean look while preserving original charts
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = CAT_PALETTE
PLOT_FONT = dict(family="Inter, sans-serif", size=12, color=BROWN_DARK)

# Subtle global CSS to uplift the UI to a modern executive look
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@600;700&family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"]  {{ font-family: 'Inter', sans-serif; color: {BROWN_DARK}; }}
h1, h2, h3 {{ font-family: 'Fraunces', serif !important; color: {BROWN_DARK}; }}
.stApp {{ background-color: #FAF7F2; }}
[data-testid="stMetric"] {{
    background-color: #FFFFFF; border: 1px solid #E7DFD3; border-left: 6px solid {GOLD};
    border-radius: 12px; padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}}
[data-testid="stMetricLabel"] {{ color: #7A6656; font-weight: 700; font-size: 0.78rem; text-transform: uppercase; letter-spacing: .06em; }}
[data-testid="stMetricValue"] {{ color: {BROWN_DARK}; font-weight: 800; font-size: 1.25rem; }}
section[data-testid="stSidebar"] {{ background-color: #FFFFFF; border-right: 1px solid #E7DFD3; padding: 18px; }}
.roast-rule {{ height: 6px; width: 84px; border-radius: 3px; margin: 10px 0 22px 0;
    background: linear-gradient(90deg, #E8D4B8, {TAN}, #8A5A32, {BROWN_DARK}); }}

.exec-header {{ display:flex; align-items:center; gap:18px; margin-bottom:6px; }}
.exec-badge {{ background: linear-gradient(90deg, rgba(212,168,83,0.12), rgba(212,168,83,0.05)); padding:10px 14px; border-radius:10px; color:{BROWN_DARK}; font-weight:800; letter-spacing:.03em; }}
.small-muted {{ color:#7A6656; font-size:0.95rem; }}

.kpi-card {{
    background: #FFFFFF; border: 1px solid #E7DFD3; border-radius: 12px; padding: 14px;
    display:flex; flex-direction:column; gap:6px; min-height:78px;
}}
.kpi-value {{ color: {BROWN_DARK}; font-weight:800; font-size:1.2rem; }}
.kpi-label {{ color:#7A6656; font-weight:700; font-size:0.78rem; text-transform:uppercase; letter-spacing:.04em; }}

.footer {{
    padding: 18px 6px; color: #6b5e51; font-size:0.92rem; border-top:1px solid #E7DFD3; margin-top:18px;
}}
.card-shadow {{ box-shadow: 0 6px 18px rgba(45,35,21,0.06); border-radius:12px; }}

.insight {{
    background: #fffdf9; border-left: 4px solid {TAN}; padding:10px 14px; border-radius:8px; margin-top:8px; color:#6f5f50;
}}
</style>
""",
    unsafe_allow_html=True,
)

DATA_DIR = Path(__file__).parent / "data"

# ---------------------------------------------------------------------------
# DATA LOADING & CLEANING
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    """Load CSVs from the data/ folder and apply light cleaning to store names."""
    fact = pd.read_csv(DATA_DIR / "coffee_features.csv")
    prod_master = pd.read_csv(DATA_DIR / "product_summary.csv")
    store_master = pd.read_csv(DATA_DIR / "store_summary.csv")

    def fix_store(n):
        return "Hell's Kitchen" if str(n).strip().lower() == "hell's kitchen" else str(n).strip()

    fact["store_location"] = fact["store_location"].apply(fix_store)
    store_master["store_location"] = store_master["store_location"].apply(fix_store)
    return fact, prod_master, store_master

# Load data once (logic unchanged)
fact, prod_master, store_master = load_data()

# Keep stable lists for filters
ALL_STORES = sorted(fact["store_location"].unique())
ALL_CATEGORIES = sorted(fact["product_category"].unique())

# ---------------------------------------------------------------------------
# SIDEBAR — FILTER CONTROLS (unchanged behavior)
# ---------------------------------------------------------------------------
st.sidebar.markdown("### ☕ Afficionado Coffee Roasters")
st.sidebar.caption("Sales Intelligence — Filters")
st.sidebar.markdown("---")

# Reset helper (unchanged)
def reset_filters():
    for k in ["f_stores", "f_categories", "f_types", "f_topn"]:
        if k in st.session_state:
            del st.session_state[k]

# Store & category selectors (same controls and keys)
st.sidebar.multiselect("Store Location", ALL_STORES, default=ALL_STORES, key="f_stores")
st.sidebar.multiselect("Product Category", ALL_CATEGORIES, default=ALL_CATEGORIES, key="f_categories")

# Derive types available based on selected categories (same logic)
types_available = sorted(
    fact.loc[fact["product_category"].isin(st.session_state.f_categories), "product_type"].unique()
)
# keep only still-valid selections when category changes; default to all available
prior_types = st.session_state.get("f_types", types_available)
valid_default = [t for t in prior_types if t in types_available] or types_available
st.sidebar.multiselect("Product Type", types_available, default=valid_default, key="f_types")

st.sidebar.slider("Top-N Products (for charts below)", min_value=3, max_value=30, value=10, key="f_topn")

st.sidebar.markdown("---")
st.sidebar.button("↺ Reset all filters", on_click=reset_filters, width="stretch")

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data: single-year transaction log across 3 NYC cafés — Lower Manhattan, Hell's Kitchen, Astoria."
)

# ---------------------------------------------------------------------------
# APPLY FILTERS — create a filtered transactions frame (identical)
# ---------------------------------------------------------------------------
def apply_filters(df):
    return df[
        df["store_location"].isin(st.session_state.f_stores)
        & df["product_category"].isin(st.session_state.f_categories)
        & df["product_type"].isin(st.session_state.f_types)
    ].copy()

filtered = apply_filters(fact)
TOP_N = st.session_state.f_topn

# If no data, surfacing a friendly message
if filtered.empty:
    st.warning("No data matches the current filter selection. Try widening your filters in the sidebar.")
    st.stop()

# ---------------------------------------------------------------------------
# AGGREGATIONS (PRODUCT-LEVEL) — identical calculations to original
# ---------------------------------------------------------------------------
prod_agg = (
    filtered.groupby(["product_id", "product_detail", "product_category", "product_type"], as_index=False)
    .agg(revenue=("revenue", "sum"), units=("transaction_qty", "sum"), transactions=("transaction_id", "count"))
)
prod_agg["avg_price"] = prod_agg["revenue"] / prod_agg["units"].replace(0, pd.NA)
prod_agg = prod_agg.merge(prod_master[["product_id", "abc_class", "segment"]], on="product_id", how="left")

total_rev_all = prod_agg["revenue"].sum()
prod_agg["revenue_pct"] = prod_agg["revenue"] / total_rev_all if total_rev_all else 0
prod_agg = prod_agg.sort_values("revenue", ascending=False).reset_index(drop=True)
prod_agg["revenue_rank"] = prod_agg["revenue"].rank(ascending=False, method="dense").astype(int)
prod_agg["cum_revenue_pct"] = prod_agg["revenue"].cumsum() / total_rev_all if total_rev_all else 0
prod_agg["volume_rank"] = prod_agg["units"].rank(ascending=False, method="dense").astype(int)
prod_agg["rank_delta"] = prod_agg["volume_rank"] - prod_agg["revenue_rank"]

# ---------------------------------------------------------------------------
# PAGE HEADER (Executive style)
# ---------------------------------------------------------------------------
header_col1, header_col2 = st.columns([8, 2])
with header_col1:
    st.markdown(
        """
    <div class='exec-header'>
      <div>
        <div class='exec-badge'>Afficionado — Sales Intelligence</div>
        <h1 style='margin:6px 0 0 0;'>How the roastery is performing</h1>
        <div class='small-muted'>Product Optimization & Revenue Contribution Analysis</div>
      </div>
    </div>
    <div class='roast-rule'></div>
    """,
        unsafe_allow_html=True,
    )
with header_col2:
    st.write("")
    st.caption("Afficionado Coffee Roasters")

# ---------------------------------------------------------------------------
# KPI ROW — preserve original KPI calculations and presentation (but improved layout)
# ---------------------------------------------------------------------------
total_revenue = filtered["revenue"].sum()
total_products = filtered["product_id"].nunique()
total_txns = len(filtered)
total_units = filtered["transaction_qty"].sum()
aov = total_revenue / total_txns if total_txns else 0

# Enhanced KPI cards for executive look (values unchanged)
k1, k2, k3, k4, k5 = st.columns([1.6, 1.4, 1.4, 1.6, 1.2])
with k1:
    st.markdown(
        f"""
        <div class="kpi-card card-shadow">
            <div class="kpi-label">Total Revenue</div>
            <div class="kpi-value">${total_revenue:,.0f}</div>
            <div class="small-muted">Revenue across selected filters</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        f"""
        <div class="kpi-card card-shadow">
            <div class="kpi-label">Total Transactions</div>
            <div class="kpi-value">{total_txns:,}</div>
            <div class="small-muted">Customer transactions</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        f"""
        <div class="kpi-card card-shadow">
            <div class="kpi-label">Units Sold</div>
            <div class="kpi-value">{total_units:,}</div>
            <div class="small-muted">Total items sold</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k4:
    st.markdown(
        f"""
        <div class="kpi-card card-shadow">
            <div class="kpi-label">Average Order Value</div>
            <div class="kpi-value">${aov:,.2f}</div>
            <div class="small-muted">Avg revenue per transaction</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k5:
    st.markdown(
        f"""
        <div class="kpi-card card-shadow">
            <div class="kpi-label">Products in View</div>
            <div class="kpi-value">{total_products}</div>
            <div class="small-muted">Unique SKUs included</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# ---------------------------------------------------------------------------
# EXECUTIVE SUMMARY
# - High-level bullets to contextualize the dashboard for an executive review.
# ---------------------------------------------------------------------------
with st.container():
    st.markdown("### Executive Summary")
    exec_left, exec_right = st.columns([3, 1])
    # compute some short summary insights (based on current filters and aggregations)
    # These computations use the same aggregated sources already present; they do not alter original calculations.
    cat_rev = filtered.groupby("product_category", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
    top_category = cat_rev.iloc[0]["product_category"] if not cat_rev.empty else "N/A"
    top_cat_share = (cat_rev.iloc[0]["revenue"] / total_revenue) * 100 if total_revenue else 0

    store_rev = filtered.groupby("store_location", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
    top_store = store_rev.iloc[0]["store_location"] if not store_rev.empty else "N/A"
    top_store_share = (store_rev.iloc[0]["revenue"] / total_revenue) * 100 if total_revenue else 0

    hour_rev = filtered.groupby("hour", as_index=False)["revenue"].sum()
    peak_hour = int(hour_rev.loc[hour_rev["revenue"].idxmax(), "hour"]) if not hour_rev.empty else None

    med_units = prod_agg["units"].median() if not prod_agg.empty else 0
    med_rev = prod_agg["revenue"].median() if not prod_agg.empty else 0

    with exec_left:
        st.markdown(
            f"""
- Total revenue for the selected view is **${total_revenue:,.0f}**, generated across **{total_txns:,}** transactions and **{total_products}** SKUs.
- Top category: **{top_category}**, contributing **{top_cat_share:.1f}%** of revenue in the current filter.
- Highest-performing store: **{top_store}**, with **{top_store_share:.1f}%** of revenue.
- Peak trading hour (selected filters): **{peak_hour:02d}:00**.
- Product distribution: median units = **{med_units:.0f}**, median product revenue = **${med_rev:,.0f}** — used in quadrant segmentation (Hero / Premium / Long Tail / Underperforming).
"""
        )
    with exec_right:
        # Executive actionables / ATS-friendly skills and deliverables
        st.markdown(
            """
            <div class="kpi-card">
                <div class="kpi-label">Recommended focus</div>
                <div style="font-weight:700; font-size:1rem; margin-top:6px;">Optimize top SKUs & pricing</div>
                <div class="small-muted" style="margin-top:8px;">Focus on improving availability of Hero items and re-evaluate underperforming SKUs.</div>
            </div>
            <div style="height:10px"></div>
            <div class="kpi-card">
                <div class="kpi-label">Portfolio-ready</div>
                <div style="font-weight:700; font-size:0.95rem; margin-top:6px;">Skills: SQL • Python • pandas • Plotly • Streamlit</div>
                <div class="small-muted" style="margin-top:8px;">Deliverables: Executive summary, KPIs, product-level analytics, Pareto analysis.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")

# ---------------------------------------------------------------------------
# Tabs — organize the full set of visualizations (no chart removals)
# ---------------------------------------------------------------------------
tab_overview, tab_products, tab_pareto, tab_table = st.tabs(
    ["📊 Overview", "🏆 Product Analysis", "📈 Pareto & Segmentation", "🔍 Data Table"]
)

# ===================== TAB 1: OVERVIEW =====================
with tab_overview:
    left_col, right_col = st.columns([1.4, 1])

    # Revenue by Category
    with left_col:
        st.subheader("Revenue by Category")
        cat_rev = filtered.groupby("product_category", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
        fig_cat = px.bar(
            cat_rev,
            x="revenue",
            y="product_category",
            orientation="h",
            color="product_category",
            color_discrete_sequence=CAT_PALETTE,
            labels={"revenue": "Revenue ($)", "product_category": ""},
        )
        fig_cat.update_layout(
            showlegend=False,
            yaxis={"categoryorder": "total ascending"},
            height=380,
            plot_bgcolor="white",
            margin=dict(l=8, r=8, t=18, b=8),
            font=PLOT_FONT,
        )
        st.plotly_chart(fig_cat, use_container_width=True)

        # Business insight for category chart
        if not cat_rev.empty:
            top_cat = cat_rev.iloc[0]
            top_cat_share = (top_cat["revenue"] / cat_rev["revenue"].sum()) * 100 if cat_rev["revenue"].sum() else 0
            st.markdown(
                f"<div class='insight'><strong>Insight:</strong> {top_cat['product_category']} is the lead revenue contributor at ${top_cat['revenue']:,.0f} ({top_cat_share:.1f}% of category revenue). Consider trade promotions or bundling strategies to protect margin.</div>",
                unsafe_allow_html=True,
            )

    # Revenue by Store
    with right_col:
        st.subheader("Revenue by Store")
        store_rev = filtered.groupby("store_location", as_index=False)["revenue"].sum()
        fig_store = px.pie(
            store_rev,
            names="store_location",
            values="revenue",
            hole=0.55,
            color="store_location",
            color_discrete_map={"Lower Manhattan": BROWN, "Hell's Kitchen": TAN, "Astoria": TERRACOTTA},
        )
        fig_store.update_layout(height=380, margin=dict(l=8, r=8, t=18, b=8), font=PLOT_FONT)
        st.plotly_chart(fig_store, use_container_width=True)

        # Business insight for store chart
        if not store_rev.empty:
            lead_store = store_rev.sort_values("revenue", ascending=False).iloc[0]
            share = (lead_store["revenue"] / store_rev["revenue"].sum()) * 100 if store_rev["revenue"].sum() else 0
            st.markdown(
                f"<div class='insight'><strong>Insight:</strong> {lead_store['store_location']} accounts for ${lead_store['revenue']:,.0f} ({share:.1f}%) of revenue in view. Operational focus there may yield the highest marginal gains.</div>",
                unsafe_allow_html=True,
            )

    # Revenue by Time Slot
    st.subheader("Revenue by Time Slot")
    slot_order = ["Morning", "Afternoon", "Evening", "Night"]
    slot_rev = filtered.groupby("time_slot", as_index=False)["revenue"].sum()
    slot_rev["time_slot"] = pd.Categorical(slot_rev["time_slot"], categories=slot_order, ordered=True)
    slot_rev = slot_rev.sort_values("time_slot")
    fig_slot = px.bar(
        slot_rev,
        x="time_slot",
        y="revenue",
        color="time_slot",
        color_discrete_map={"Morning": GOLD, "Afternoon": BROWN, "Evening": BROWN_DARK, "Night": BLUE},
        labels={"revenue": "Revenue ($)", "time_slot": ""},
    )
    fig_slot.update_layout(showlegend=False, height=320, plot_bgcolor="white", margin=dict(l=8, r=8, t=18, b=8), font=PLOT_FONT)
    st.plotly_chart(fig_slot, use_container_width=True)

    # Business insight for time slot
    if not slot_rev.empty:
        lead_slot = slot_rev.sort_values("revenue", ascending=False).iloc[0]
        st.markdown(
            f"<div class='insight'><strong>Insight:</strong> Peak revenue by time slot is <strong>{lead_slot['time_slot']}</strong> with ${lead_slot['revenue']:,.0f}. Consider targeted promotions, staffing, and product preparedness for this slot.</div>",
            unsafe_allow_html=True,
        )

    # Peak hour caption (unchanged logic)
    hour_rev = filtered.groupby("hour", as_index=False)["revenue"].sum()
    peak_hour = int(hour_rev.loc[hour_rev["revenue"].idxmax(), "hour"]) if not hour_rev.empty else None
    st.caption(f"⏰ Peak trading hour in the current filter selection: **{peak_hour:02d}:00**")

# ===================== TAB 2: PRODUCT ANALYSIS =====================
with tab_products:
    top_rev = prod_agg.nsmallest(TOP_N, "revenue_rank")
    top_vol = prod_agg.nsmallest(TOP_N, "volume_rank")
    bottom_rev = prod_agg.nlargest(TOP_N, "revenue_rank")

    # Top revenue and top volume side-by-side
    c1, c2 = st.columns(2)
    with c1:
        st.subheader(f"Top {TOP_N} Products — Revenue")
        fig_top_rev = px.bar(
            top_rev.sort_values("revenue"),
            x="revenue",
            y="product_detail",
            orientation="h",
            color="segment",
            color_discrete_map=SEG_COLORS,
            labels={"revenue": "Revenue ($)", "product_detail": ""},
        )
        fig_top_rev.update_layout(height=420, plot_bgcolor="white", margin=dict(l=8, r=8, t=18, b=8), legend=dict(orientation="h", yanchor="bottom", y=1.02), font=PLOT_FONT)
        st.plotly_chart(fig_top_rev, use_container_width=True)

        # Insight for top revenue products
        if not top_rev.empty:
            lead = top_rev.sort_values("revenue", ascending=False).iloc[0]
            st.markdown(
                f"<div class='insight'><strong>Insight:</strong> Highest revenue SKU: <strong>{lead['product_detail']}</strong> — ${lead['revenue']:,.0f}. Evaluate inventory and promotional placement to preserve revenue share.</div>",
                unsafe_allow_html=True,
            )

    with c2:
        st.subheader(f"Top {TOP_N} Products — Units Sold")
        fig_top_vol = px.bar(
            top_vol.sort_values("units"),
            x="units",
            y="product_detail",
            orientation="h",
            color="segment",
            color_discrete_map=SEG_COLORS,
            labels={"units": "Units Sold", "product_detail": ""},
        )
        fig_top_vol.update_layout(height=420, plot_bgcolor="white", margin=dict(l=8, r=8, t=18, b=8), legend=dict(orientation="h", yanchor="bottom", y=1.02), font=PLOT_FONT)
        st.plotly_chart(fig_top_vol, use_container_width=True)

        # Insight for top volume products
        if not top_vol.empty:
            lead_v = top_vol.sort_values("units", ascending=False).iloc[0]
            st.markdown(
                f"<div class='insight'><strong>Insight:</strong> Highest-volume SKU: <strong>{lead_v['product_detail']}</strong> — {lead_v['units']:,} units. Cross-sell opportunities could increase AOV.</div>",
                unsafe_allow_html=True,
            )

    # Bottom products
    st.subheader(f"Bottom {TOP_N} Products — Revenue")
    fig_bottom = px.bar(
        bottom_rev.sort_values("revenue", ascending=False),
        x="revenue",
        y="product_detail",
        orientation="h",
        color_discrete_sequence=[RED],
        labels={"revenue": "Revenue ($)", "product_detail": ""},
    )
    fig_bottom.update_layout(height=340, plot_bgcolor="white", margin=dict(l=8, r=8, t=18, b=8), showlegend=False, font=PLOT_FONT)
    st.plotly_chart(fig_bottom, use_container_width=True)

    # Insight for bottom sellers
    if not bottom_rev.empty:
        st.markdown(
            f"<div class='insight'><strong>Insight:</strong> Bottom {TOP_N} products cumulatively contribute ${(bottom_rev['revenue'].sum()):,.0f}. Consider delisting or promotional testing to recover shelf space.</div>",
            unsafe_allow_html=True,
        )

    # Popularity vs Revenue scatter
    st.subheader("Popularity vs. Revenue")
    st.caption("Each dot is a product. Dashed lines mark the median units and median revenue in the current filter — the four quadrants correspond to Hero / Premium / Long Tail / Underperforming.")
    med_units = prod_agg["units"].median()
    med_rev = prod_agg["revenue"].median()
    fig_scatter = px.scatter(
        prod_agg,
        x="units",
        y="revenue",
        color="segment",
        color_discrete_map=SEG_COLORS,
        hover_name="product_detail",
        size_max=12,
        labels={"units": "Units Sold (popularity)", "revenue": "Revenue ($)"},
    )
    fig_scatter.add_vline(x=med_units, line_dash="dash", line_color=TAN)
    fig_scatter.add_hline(y=med_rev, line_dash="dash", line_color=TAN)
    fig_scatter.update_traces(marker=dict(size=10, line=dict(width=1, color="white")))
    fig_scatter.update_layout(height=460, plot_bgcolor="white", margin=dict(l=8, r=8, t=18, b=8), font=PLOT_FONT)
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Insight summarizing segment counts
    seg_counts = prod_agg["segment"].value_counts().to_dict()
    seg_insight_parts = []
    for seg_name in ["Hero", "Premium", "Long Tail", "Underperforming"]:
        seg_insight_parts.append(f"{seg_name}: {seg_counts.get(seg_name,0)}")
    st.markdown(
        f"<div class='insight'><strong>Insight:</strong> Segment distribution — {', '.join(seg_insight_parts)}. Prioritize 'Hero' products for margin protection and 'Long Tail' products for catalog rationalization.</div>",
        unsafe_allow_html=True,
    )

# ===================== TAB 3: PARETO & SEGMENTATION =====================
with tab_pareto:
    c1, c2, c3, c4 = st.columns(4)
    n80 = int((prod_agg["cum_revenue_pct"] <= 0.80).sum()) + 1
    top20_n = max(1, int(round(len(prod_agg) * 0.2)))
    top20_share = prod_agg.nsmallest(top20_n, "revenue_rank")["revenue"].sum() / total_rev_all if total_rev_all else 0
    c1.metric("Products to reach 80% revenue", f"{n80} / {len(prod_agg)}")
    c2.metric("Top 20% revenue share", f"{top20_share*100:.1f}%")
    c3.metric("Class A products", int((prod_agg['abc_class'] == 'A').sum()))
    c4.metric("Class C products", int((prod_agg['abc_class'] == 'C').sum()))

    st.subheader("Pareto Chart — Cumulative Revenue Concentration")
    pareto = prod_agg.sort_values("revenue_rank")
    fig = go.Figure()
    fig.add_bar(x=pareto["product_detail"], y=pareto["revenue"], name="Revenue", marker_color=BROWN, yaxis="y1")
    fig.add_trace(
        go.Scatter(
            x=pareto["product_detail"],
            y=pareto["cum_revenue_pct"] * 100,
            name="Cumulative %",
            yaxis="y2",
            line=dict(color=BLUE, width=2),
        )
    )
    fig.add_hline(y=80, line_dash="dash", line_color=RED, yref="y2")
    fig.update_layout(
        height=420,
        plot_bgcolor="white",
        margin=dict(l=8, r=8, t=18, b=8),
        xaxis=dict(showticklabels=False, title="Products (ranked by revenue)"),
        yaxis=dict(title="Revenue ($)"),
        yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 100]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        font=PLOT_FONT,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"<div class='insight'><strong>Insight:</strong> {n80} products (of {len(prod_agg)}) are required to reach ~80% of cumulative revenue. The top {top20_n} products account for {top20_share*100:.1f}% of revenue — prime candidates for assortment optimization.</div>",
        unsafe_allow_html=True,
    )

    # ABC & Segmentation charts
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("ABC Classification")
        abc_rev = prod_agg.groupby("abc_class", as_index=False)["revenue"].sum()
        fig_abc = px.bar(
            abc_rev,
            x="abc_class",
            y="revenue",
            color="abc_class",
            color_discrete_map=ABC_COLORS,
            labels={"revenue": "Revenue ($)", "abc_class": "ABC Class"},
        )
        fig_abc.update_layout(height=340, plot_bgcolor="white", showlegend=False, margin=dict(l=8, r=8, t=18, b=8), font=PLOT_FONT)
        st.plotly_chart(fig_abc, use_container_width=True)

        # ABC insight
        top_class = abc_rev.sort_values("revenue", ascending=False).iloc[0] if not abc_rev.empty else None
        if top_class is not None:
            st.markdown(
                f"<div class='insight'><strong>Insight:</strong> ABC analysis shows class <strong>{top_class['abc_class']}</strong> contributes the largest revenue bucket (${top_class['revenue']:,.0f}). Use ABC to prioritize inventory governance.</div>",
                unsafe_allow_html=True,
            )

    with c2:
        st.subheader("Product Segmentation")
        seg_rev = prod_agg.groupby("segment", as_index=False)["revenue"].sum()
        fig_seg = px.bar(
            seg_rev,
            x="segment",
            y="revenue",
            color="segment",
            color_discrete_map=SEG_COLORS,
            labels={"revenue": "Revenue ($)", "segment": ""},
        )
        fig_seg.update_layout(height=340, plot_bgcolor="white", showlegend=False, margin=dict(l=8, r=8, t=18, b=8), font=PLOT_FONT)
        st.plotly_chart(fig_seg, use_container_width=True)

        # Segmentation insight
        if not seg_rev.empty:
            seg_lead = seg_rev.sort_values("revenue", ascending=False).iloc[0]
            st.markdown(
                f"<div class='insight'><strong>Insight:</strong> Segment leader: <strong>{seg_lead['segment']}</strong> — ${seg_lead['revenue']:,.0f}. Align assortment and promotions to grow premium and hero segments.</div>",
                unsafe_allow_html=True,
            )

# ===================== TAB 4: DATA TABLE =====================
with tab_table:
    st.subheader("Product Drill-Down Table")
    search = st.text_input("🔍 Search product name")
    show = prod_agg.copy()
    if search:
        show = show[show["product_detail"].str.contains(search, case=False, na=False)]

    show_display = show[
        [
            "product_detail",
            "product_category",
            "product_type",
            "revenue",
            "units",
            "avg_price",
            "revenue_pct",
            "revenue_rank",
            "volume_rank",
            "rank_delta",
            "abc_class",
            "segment",
        ]
    ].rename(
        columns={
            "product_detail": "Product",
            "product_category": "Category",
            "product_type": "Type",
            "revenue": "Revenue",
            "units": "Units",
            "avg_price": "Avg Price",
            "revenue_pct": "Rev %",
            "revenue_rank": "Rev Rank",
            "volume_rank": "Sales Rank",
            "rank_delta": "Δ Rank",
            "abc_class": "ABC",
            "segment": "Segment",
        }
    ).sort_values("Rev Rank")
    show_display["Rev %"] = (show_display["Rev %"] * 100).round(2)

    # Use Streamlit's column_config for nicer formatting (keeps calculations unchanged)
    st.dataframe(
        show_display,
        use_container_width=True,
        hide_index=True,
        height=460,
        column_config={
            "Revenue": st.column_config.NumberColumn(format="$%.0f"),
            "Avg Price": st.column_config.NumberColumn(format="$%.2f"),
            "Rev %": st.column_config.ProgressColumn(
                format="%.1f%%", min_value=0.0, max_value=float(show_display["Rev %"].max()) if len(show_display) else 1.0
            ),
        },
    )

    csv = show_display.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Download this table as CSV", csv, "product_performance.csv", "text/csv")

    st.markdown(
        "<div class='insight'><strong>How to use this table:</strong> Sort by Rev Rank or Sales Rank to prioritize SKU reviews. Use the Δ Rank column to identify products where sales volume and revenue disagree — good candidates for pricing or promotion review.</div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# FOOTER — improved with project information & ATS-friendly details
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    """
<div class="footer">
<div style="display:flex; justify-content:space-between; gap:12px; align-items:flex-start; flex-wrap:wrap;">
    <div style="max-width:70%;">
        <strong>Afficionado Coffee Roasters · Sales Intelligence Dashboard</strong><br>
        This dashboard was built for portfolio presentation and executive review. It includes product-level revenue and volume analysis, ABC classification, Pareto concentration, and segmentation to guide merchandising and pricing decisions.
    </div>
    <div style="min-width:280px;">
        <strong>Project details (portfolio / ATS friendly)</strong>
        <ul style="margin:6px 0 0 18px;">
            <li>Role: Data Analyst / Data Scientist — EDA, aggregation, visualization, dashboarding</li>
            <li>Tech: Python, pandas, Plotly, Streamlit</li>
            <li>Deliverables: Executive summary, KPIs, product analytics, Pareto analysis, downloadable CSV</li>
        </ul>
    </div>
</div>
<div style="margin-top:10px; color:#7a6656; font-size:0.9rem;">
    Repository: <a href="https://github.com/Bhargav227/afficionado" target="_blank">github.com/Bhargav227/afficionado</a> · Data: synthetic/sampled single-year transaction log · Built with Streamlit · © Afficionado
</div>
</div>
""",
    unsafe_allow_html=True,
)
