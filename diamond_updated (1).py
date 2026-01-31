# -*- coding: utf-8 -*-
"""
Diamonds — Production + Trade Supply Chain (Streamlit)

✅ Production (Kimberley Process) module is kept EXACTLY as you gave it (ordering fix preserved).
🆕 Trade (HS 7102) is split into TWO modules:
  1) Rough Diamonds
     - Unsorted: 710210 + 710231
     - Sorted:   710221
  2) Cut & Polished Diamonds
     - Industrial:     710229
     - Non-industrial: 710239

Each HS6 sheet contains BOTH imports and exports blocks. We parse directly from those sheets.
Shares are computed using the "World" row in each sheet (as you asked).
"""

from __future__ import annotations

import re
import html
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


# -----------------------------
# Helpers (kept from your working Production build)
# -----------------------------
def apply_theme() -> None:
    st.markdown(
        """
<style>
@import url("https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap");

:root {
  --bg: #f4f7fb;
  --panel: #ffffff;
  --panel-soft: #f0f4f9;
  --text: #1c2430;
  --muted: #5a6b82;
  --accent: #0b6ea8;
  --accent-strong: #115d86;
  --accent-soft: #e1f1fb;
  --border: #d7e1ee;
  --shadow: 0 18px 40px rgba(16, 31, 55, 0.12);
  --shadow-soft: 0 10px 22px rgba(18, 30, 50, 0.08);
  --primary-color: #0b6ea8;
  --accent-color: #0b6ea8;
}

html, body, [class*="css"] {
  font-family: "Manrope", sans-serif;
  color: var(--text);
}

.stApp {
  background:
    radial-gradient(1200px 600px at 8% -10%, #eaf2fb 0%, transparent 60%),
    radial-gradient(900px 500px at 92% -10%, #e7f5f1 0%, transparent 55%),
    linear-gradient(180deg, #f7f9fc 0%, #f1f5fa 100%);
}

.block-container {
  padding-top: 2rem;
  padding-bottom: 2.5rem;
  max-width: 1400px;
  animation: fadeIn 0.6s ease-out both;
}

h1, h2, h3, h4 {
  font-family: "Playfair Display", serif;
  letter-spacing: 0.2px;
  color: var(--text);
}

h1 {
  font-size: 2.6rem;
}

[data-testid="stCaptionContainer"] {
  color: var(--muted);
  font-size: 0.95rem;
  margin-top: -0.35rem;
}

section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #eff4fb 0%, #ecf1f7 100%);
  border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {
  color: var(--text);
}

section[data-testid="stSidebar"] .stRadio > div {
  padding: 0.35rem 0.25rem;
  border-radius: 12px;
  background: #f6f9fc;
  border: 1px solid var(--border);
}

[data-testid="stMetric"] {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 14px 16px;
  box-shadow: var(--shadow-soft);
}

[data-testid="stMetric"] > div {
  align-items: flex-start;
}

[data-testid="stMetricLabel"] {
  color: var(--muted);
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

[data-testid="stMetricValue"] {
  font-size: 1.6rem;
  font-weight: 700;
  white-space: normal !important;
  overflow: visible !important;
  text-overflow: unset !important;
  word-break: break-word !important;
  line-height: 1.15;
}


/* Custom metric card (for long text like Top Producer) */
.metric-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 14px 16px;
  box-shadow: var(--shadow-soft);
  height: 100%;
}
.metric-card .label {
  color: var(--muted);
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.metric-card .value {
  margin-top: 6px;
  font-size: 1.15rem;
  font-weight: 750;
  line-height: 1.2;
  white-space: normal;
  word-break: break-word;
}

/* Force accent for native controls */
input[type="radio"], input[type="checkbox"] {
  accent-color: var(--accent) !important;
}

/* Multi-select tag chips */
div[data-baseweb="tag"] {
  background: rgba(11, 110, 168, 0.14) !important;
  border: 1px solid rgba(11, 110, 168, 0.28) !important;
}
div[data-baseweb="tag"] span {
  color: var(--accent-strong) !important;
  font-weight: 650 !important;
}
div[data-baseweb="tag"] svg {
  color: var(--accent-strong) !important;
}



.stTabs [data-baseweb="tab-list"] {
  gap: 0.35rem;
  padding: 0.2rem;
  background: var(--panel-soft);
  border-radius: 999px;
  border: 1px solid var(--border);
}

.stTabs [data-baseweb="tab"] {
  background: transparent;
  border-radius: 999px;
  padding: 0.45rem 1rem;
  color: var(--muted);
  font-weight: 600;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
  background: var(--accent-soft);
  color: var(--accent-strong);
}

div[data-testid="stDataFrame"] {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 6px;
  box-shadow: var(--shadow-soft);
}

div.stPlotlyChart {
  background: var(--panel);
  border-radius: 16px;
  padding: 6px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-soft);
}

div[data-baseweb="select"] > div {
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--panel);
}

.stButton > button {
  border-radius: 12px;
  border: 1px solid var(--accent-strong);
  background: linear-gradient(140deg, #0b6ea8 0%, #0f8bb4 100%);
  color: #ffffff;
  font-weight: 600;
  padding: 0.45rem 1rem;
  box-shadow: 0 12px 22px rgba(11, 110, 168, 0.18);
}

.stButton > button:hover {
  border-color: #0a5a87;
  background: linear-gradient(140deg, #0a5a87 0%, #0b6ea8 100%);
}


/* Subtle hover lift for a more "premium" dashboard feel */
[data-testid="stMetric"], .metric-card, div.stPlotlyChart, div[data-testid="stDataFrame"] {
  transition: transform 120ms ease, box-shadow 120ms ease;
}
[data-testid="stMetric"]:hover, .metric-card:hover, div.stPlotlyChart:hover, div[data-testid="stDataFrame"]:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}


/* Hero header */
.hero {
  position: relative;
  border-radius: 22px;
  border: 1px solid rgba(11, 110, 168, 0.22);
  background:
    radial-gradient(1200px 280px at 15% -20%, rgba(11,110,168,0.28) 0%, transparent 60%),
    radial-gradient(900px 260px at 85% -30%, rgba(15,139,180,0.22) 0%, transparent 58%),
    linear-gradient(110deg, rgba(255,255,255,0.98) 0%, rgba(245,249,252,0.96) 60%, rgba(233,244,251,0.96) 100%);
  box-shadow: var(--shadow-soft);
  padding: 20px 22px;
  overflow: hidden;
  margin-bottom: 0.85rem;
}
.hero:after {
  content: "";
  position: absolute;
  right: -120px;
  top: -140px;
  width: 420px;
  height: 420px;
  background: radial-gradient(circle at 30% 30%, rgba(11,110,168,0.22), transparent 60%);
  transform: rotate(18deg);
}
.hero-row {
  position: relative;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  z-index: 2;
}
.hero-left { min-width: 0; }
.hero-title {
  margin: 0;
  font-family: "Playfair Display", serif;
  font-weight: 700;
  font-size: 2.05rem;
  letter-spacing: 0.2px;
  color: var(--text);
}
.hero-subtitle {
  margin-top: 6px;
  color: var(--muted);
  font-size: 0.98rem;
  line-height: 1.35;
}
.hero-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(11,110,168,0.14);
  border: 1px solid rgba(11,110,168,0.22);
  color: var(--accent-strong);
  font-weight: 650;
  font-size: 0.82rem;
  white-space: nowrap;
  z-index: 2;
}
.hero-meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 10px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
""",
        unsafe_allow_html=True,
    )



def style_plotly(fig) -> None:
    """Visual-only Plotly styling. Safe to call on any Plotly figure."""
    try:
        fig.update_layout(
            template="plotly_white",
            font=dict(family="Manrope, sans-serif", size=13, color="#1c2430"),
            title_font=dict(family="Playfair Display, serif", size=20, color="#1c2430"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=60, b=10),
            legend=dict(
                bgcolor="rgba(255,255,255,0.65)",
                bordercolor="rgba(215,225,238,1)",
                borderwidth=1,
            ),
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Manrope, sans-serif"),
        )
        fig.update_xaxes(showgrid=True, gridcolor="rgba(148,163,184,0.22)", zeroline=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.16)", zeroline=False)
    except Exception:
        # Never break the app due to styling
        pass




def metric_card(label: str, value: str, *, tooltip: str | None = None) -> None:
    """Visual-only metric card used when Streamlit's st.metric truncates long text."""
    label_txt = html.escape(str(label))
    raw_val = "" if value is None else str(value)
    value_txt = html.escape(raw_val)
    tip_txt = html.escape(str(tooltip if tooltip is not None else raw_val))

    # Adaptive font size for long country names (visual-only)
    n = len(raw_val.strip())
    fs = "1.15rem"
    if n >= 18:
        fs = "1.05rem"
    if n >= 28:
        fs = "0.98rem"
    if n >= 40:
        fs = "0.92rem"

    st.markdown(
        f"""
        <div class="metric-card" title="{tip_txt}">
          <div class="label">{label_txt}</div>
          <div class="value" style="font-size:{fs};">{value_txt}</div>
        </div>
        """
        ,
        unsafe_allow_html=True,
    )



def render_hero_header(
    title: str,
    subtitle: str,
    *,
    badge: str | None = None,
    icon: str = "💎",
) -> None:
    """Render a premium header card (visual-only)."""
    title_txt = html.escape(str(title))
    subtitle_txt = html.escape(str(subtitle))
    badge_html = ""
    if badge:
        badge_html = f'<div class="hero-pill">{html.escape(str(badge))}</div>'

    st.markdown(
        f'''
        <div class="hero">
          <div class="hero-row">
            <div class="hero-left">
              <div class="hero-title">{html.escape(icon)} {title_txt}</div>
              <div class="hero-subtitle">{subtitle_txt}</div>
            </div>
            {badge_html}
          </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )


def pick_first_existing(candidates: list[str]) -> str | None:
    """Return the first existing path from candidates (checks app folder + CWD)."""
    base_dirs = []
    try:
        base_dirs.append(Path(__file__).resolve().parent)
    except Exception:
        pass
    base_dirs.append(Path.cwd())

    for p in candidates:
        # Absolute or relative
        cand0 = Path(str(p)).expanduser()
        if cand0.is_absolute() and cand0.exists():
            return str(cand0)
        for base in base_dirs:
            cand = (base / str(p)).expanduser()
            if cand.exists():
                return str(cand)
        if cand0.exists():
            return str(cand0)
    return None

@st.cache_data(show_spinner=False)
def load_excel(path: str) -> pd.DataFrame:
    return pd.read_excel(path)


def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    # drop fully empty columns (e.g., 'Unnamed: ...')
    df = df.loc[:, ~df.columns.astype(str).str.match(r"^Unnamed")]
    # strip whitespace from string columns
    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].astype(str).str.strip()
        df.loc[df[c].isin(["nan", "None", "NaN", ""]), c] = np.nan
    return df


def _period_label(year: int, quarter: int) -> str:
    return f"{int(year)} H1" if int(quarter) == 1 else f"{int(year)} H2"


def _usd_scale_choice_production() -> tuple[str, float]:
    """
    Production 'US Value' in the source file is **absolute USD**.
    This returns (label, divisor) for DISPLAY ONLY:
      - USD Mn: divide by 1e6
      - USD Bn: divide by 1e9
    """
    scale = st.radio(
        "US Value display unit (Production — scaling only)",
        ["USD (Absolute)", "USD Mn", "USD Bn"],
        index=1,
        horizontal=True,
        key="prod_usd_scale_main",
    )
    if scale == "USD Mn":
        return "USD Mn", 1e6
    if scale == "USD Bn":
        return "USD Bn", 1e9
    return "USD", 1.0

# -----------------------------
# Production (Kimberley Process)  ✅ DO NOT TOUCH (as requested)
# -----------------------------
def _get_prod_usd_scale(selection: str) -> tuple[str, float]:
    """Map production US Value scale selection to (label, divisor)."""
    if selection == "USD Mn":
        return "USD Mn", 1e6
    if selection == "USD Bn":
        return "USD Bn", 1e9
    return "USD", 1.0


def render_prod_unit_selector(widget_key: str) -> tuple[str, float]:
    """
    Production 'US Value' in the source file is **absolute USD**.
    We allow display-only scaling (Absolute / Mn / Bn) and keep the choice synced across tabs.
    """
    options = ["USD (Absolute)", "USD Mn", "USD Bn"]
    current = st.session_state.get("prod_usd_scale", "USD Mn")
    # Normalize stored value
    if current not in options:
        current = "USD Mn"
    idx = options.index(current)

    selection = st.radio(
        "US Value display unit (Production — scaling only)",
        options,
        index=idx,
        horizontal=True,
        key=widget_key,
    )
    st.session_state["prod_usd_scale"] = selection
    return _get_prod_usd_scale(selection)


# -----------------------------
# Production (Kimberley Process)
# -----------------------------
def render_production_module() -> None:
    render_hero_header(
        title="Production",
        subtitle="Production dataset • carat & US value • scaling affects display only",
        badge="2003–2024",
        icon="💎",
    )

    # Global UI toggle (sidebar)
    show_labels = bool(st.session_state.get("show_data_labels", False))

    # Default-only workflow: no upload controls in UI
    prod_candidates = [
        "Production of Diamonds - Updated.xlsx",
        "Production of Diamonds - Updated.xls",
        "Production of Diamonds.xlsx",
    ]
    prod_path = pick_first_existing(prod_candidates)
    if prod_path is None:
        st.error("Default production file not found. Place `Production of Diamonds - Updated.xlsx` in the app folder.")
        return
    st.caption(f"File loaded: `{Path(prod_path).name}`")

    df_raw = load_excel(prod_path)
    df_raw = _clean_columns(df_raw)

    # Standardize expected columns (based on your file)
    rename_map = {
        "Country Name": "country",
        "Year": "year",
        "Quarter": "quarter",  # present in file, but we show YEARLY only
        "Trade Type": "trade_type",
        "Production Type": "production_type",
        "Carat": "carat",
        "US Value": "us_value",
    }
    df = df_raw.rename(columns=rename_map).copy()

    required = ["country", "year", "trade_type", "production_type", "carat", "us_value"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"Production file is missing required columns: {missing}")
        st.write("Found columns:", list(df.columns))
        return

    # Types
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["carat"] = pd.to_numeric(df["carat"], errors="coerce")
    df["us_value"] = pd.to_numeric(df["us_value"], errors="coerce")
    df = df.dropna(subset=["country", "year"])

    # -----------------------------
    # Sidebar filters (YEARLY only)
    # -----------------------------
    st.sidebar.subheader("Production filters")

    year_min = int(df["year"].min())
    year_max = int(df["year"].max())
    yr_lo, yr_hi = st.sidebar.slider(
        "Year range",
        min_value=year_min,
        max_value=year_max,
        value=(year_min, year_max),
        step=1,
        key="prod_year_range",
    )

    trade_types = ["All"] + sorted([x for x in df["trade_type"].dropna().unique().tolist()])
    trade_choice = st.sidebar.selectbox("Trade Type", trade_types, index=0, key="prod_trade_type")

    prod_types_all = sorted([x for x in df["production_type"].dropna().unique().tolist()])
    prod_type_choice = st.sidebar.multiselect(
        "Production Type",
        options=prod_types_all,
        default=prod_types_all,
        key="prod_prod_types",
    )

    metric_choice = st.sidebar.radio(
        "Metric",
        ["Carat", "Million Carats", "US Value (Absolute USD)", "USD per Carat"],
        index=2,
        key="prod_metric",
    )

    # Apply filters (no quarter/half-year logic)
    f = df.copy()
    f = f[(f["year"] >= yr_lo) & (f["year"] <= yr_hi)]
    if trade_choice != "All":
        f = f[f["trade_type"] == trade_choice]
    if prod_type_choice:
        f = f[f["production_type"].isin(prod_type_choice)]

    if f.empty:
        st.warning("No data after applying filters.")
        return

    # YEARLY aggregation (summing across quarters if present)
    fy = (
        f.groupby(["country", "year"], as_index=False)[["carat", "us_value"]]
        .sum()
        .sort_values(["year", "country"])
    )
    fy["usd_per_carat"] = np.where(fy["carat"] > 0, fy["us_value"] / fy["carat"], np.nan)

    # Tabs (Insights removed)
    tab_overview, tab_country, tab_data = st.tabs(["📌 Overview", "📈 Country Trend", "🧾 Data"])

    # -----------------------------
    # Overview (Top N snapshot)
    # -----------------------------
    with tab_overview:
        years_avail = sorted(fy["year"].dropna().astype(int).unique().tolist())
        if not years_avail:
            st.warning("No years available under current filters.")
            return

        # Controls row: snapshot year + Top N + Unit selector (placed ABOVE visuals)
        c1, c2, c3 = st.columns([1.25, 2.15, 1.6])
        with c1:
            snap_year = st.selectbox("Snapshot year", years_avail, index=len(years_avail) - 1, key="prod_snap_year")
        with c2:
            top_n = st.slider(
                "Top N producers (snapshot)",
                min_value=3,
                max_value=30,
                value=10,
                step=1,
                key="prod_top_n",
            )
        with c3:
            st.markdown("#### Display unit")
            st.caption("US Value is stored as **absolute USD**. Scaling affects display only.")
            usd_unit_label, usd_div = render_prod_unit_selector("prod_usd_scale_overview")

        snap = fy[fy["year"].astype(int) == int(snap_year)].copy()
        if snap.empty:
            st.warning("No data for the selected snapshot year under current filters.")
            return

        g = snap.sort_values("us_value", ascending=False).copy()
        g["us_value_disp"] = g["us_value"] / usd_div

        if metric_choice == "Carat":
            metric_label = "Carat"
            g["metric_disp"] = g["carat"]
            text_fmt = "%{x:,.0f}"
        elif metric_choice == "Million Carats":
            metric_label = "Million Carats"
            g["metric_disp"] = g["carat"] / 1_000_000
            text_fmt = "%{x:,.2f}"
        elif metric_choice == "USD per Carat":
            metric_label = "USD/Carat (USD)"
            g["metric_disp"] = g["usd_per_carat"]
            text_fmt = "%{x:,.2f}"
        else:
            metric_label = f"US Value ({usd_unit_label})"
            g["metric_disp"] = g["us_value_disp"]
            text_fmt = "%{x:,.2f}" if usd_unit_label != "USD" else "%{x:,.0f}"

        top_df = g.nlargest(int(top_n), "metric_disp").copy().sort_values("metric_disp", ascending=False)

        # KPI cards (snapshot totals)
        total_carat = float(snap["carat"].sum())
        total_usd_disp = float(snap["us_value"].sum() / usd_div)
        avg_usd_per_carat = float((snap["us_value"].sum() / snap["carat"].sum()) if snap["carat"].sum() > 0 else np.nan)
        top_producer = top_df.iloc[0]["country"] if len(top_df) else "—"

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Carat", f"{total_carat:,.0f}")
        k2.metric(f"Total US Value ({usd_unit_label})", f"{total_usd_disp:,.2f}" if usd_unit_label != "USD" else f"{total_usd_disp:,.0f}")
        k3.metric("Avg USD/Carat", f"{avg_usd_per_carat:,.2f}" if np.isfinite(avg_usd_per_carat) else "—")
        with k4:
            metric_card("Top Producer", str(top_producer), tooltip=str(top_producer))

        # --- Top producers chart ---
        title = f"Top {len(top_df)} Producers — {int(snap_year)}"
        fig = px.bar(
            top_df,
            x="metric_disp",
            y="country",
            orientation="h",
            text=("metric_disp" if show_labels else None),
            title=title,
            labels={"metric_disp": metric_label, "country": "Producer"},
        )
        if show_labels:
            fig.update_traces(textposition="auto", texttemplate=text_fmt)
        else:
            fig.update_traces(texttemplate=None)
        fig.update_yaxes(
            categoryorder="array",
            categoryarray=top_df["country"].tolist(),
            autorange="reversed",
        )
        fig.update_layout(margin=dict(l=240, r=10, t=60, b=10), height=520)
        style_plotly(fig)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Snapshot Table (Top N)")
        view = top_df[["country", "carat", "us_value_disp", "usd_per_carat"]].copy()
        view.insert(0, "rank", range(1, len(view) + 1))
        view = view.rename(
            columns={
                "country": "Producer",
                "carat": "Carat",
                "us_value_disp": f"US Value ({usd_unit_label})",
                "usd_per_carat": "USD/Carat",
            }
        )
        st.dataframe(view, use_container_width=True)
    # -----------------------------
    # Country Trend (YEARLY)
    # -----------------------------
    with tab_country:
        all_countries = sorted(fy["country"].dropna().unique().tolist())
        if not all_countries:
            st.info("No countries available under current filters.")
            return

        c1, c2 = st.columns([2.2, 1.6])
        with c1:
            default_countries = ["India"] if "India" in all_countries else [all_countries[0]]
            focus_countries = st.multiselect(
                "Select countries (trend)",
                options=all_countries,
                default=default_countries,
                key="prod_focus_countries",
            )
        with c2:
            st.markdown("#### Display unit")
            st.caption("US Value is stored as **absolute USD**. Scaling affects display only.")
            usd_unit_label, usd_div = render_prod_unit_selector("prod_usd_scale_trend")

        if not focus_countries:
            st.info("Select at least one country to view the trend.")
            return

        d = fy[fy["country"].isin(focus_countries)].copy()
        if d.empty:
            st.info("No data for the selected countries under current filters.")
            return

        d = d.sort_values(["country", "year"])
        d["us_value_disp"] = d["us_value"] / usd_div
        d["carat_mn"] = d["carat"] / 1_000_000

        if metric_choice == "Carat":
            y = "carat"
            ylab = "Carat"
        elif metric_choice == "Million Carats":
            y = "carat_mn"
            ylab = "Million Carats"
        elif metric_choice == "USD per Carat":
            y = "usd_per_carat"
            ylab = "USD/Carat (USD)"
        else:
            y = "us_value_disp"
            ylab = f"US Value ({usd_unit_label})"

        fig = px.line(
            d,
            x="year",
            y=y,
            color="country",
            markers=True,
            text=(y if show_labels else None),
            labels={"year": "Year", y: ylab, "country": "Country"},
            title=f"Country trend — {ylab}",
        )
        if show_labels:
            fig.update_traces(mode="lines+markers+text", textposition="top center")
        fig.update_layout(margin=dict(l=10, r=10, t=60, b=10), height=420)
        style_plotly(fig)
        st.plotly_chart(fig, use_container_width=True)

        show_df = d[["country", "year", "carat", "us_value_disp", "usd_per_carat"]].copy()
        show_df = show_df.rename(
            columns={
                "us_value_disp": f"US Value ({usd_unit_label})",
                "usd_per_carat": "USD/Carat",
            }
        )
        st.dataframe(show_df, use_container_width=True)

    # -----------------------------
    # Data (YEAR filter + Year columns + YoY + Top N + Downloads)
    # -----------------------------
    with tab_data:
        st.subheader("Filtered data (production) — Yearly")

        years_all = sorted(fy["year"].dropna().astype(int).unique().tolist())
        if not years_all:
            st.info("No years available under current filters.")
            return

        # Controls row: Start/End + Top N + Unit selector
        c1, c2, c3, c4 = st.columns([1.0, 1.0, 1.2, 1.6])
        with c1:
            start_year = st.selectbox("Start year", years_all, index=0, key="prod_data_start_year")
        with c2:
            end_year = st.selectbox("End year", years_all, index=len(years_all) - 1, key="prod_data_end_year")
        with c3:
            top_n_data = st.slider("Top N countries", min_value=3, max_value=50, value=10, step=1, key="prod_data_top_n")
        with c4:
            st.markdown("#### Display unit")
            st.caption("US Value is stored as **absolute USD**. Scaling affects display only.")
            usd_unit_label, usd_div = render_prod_unit_selector("prod_usd_scale_data")

        if int(start_year) > int(end_year):
            st.warning("Start year must be <= End year.")
            return

        base = fy[(fy["year"].astype(int) >= int(start_year)) & (fy["year"].astype(int) <= int(end_year))].copy()
        if base.empty:
            st.info("No data for the selected year range.")
            return

        # Rank countries for Top N selection
        if metric_choice in ["Carat", "Million Carats"]:
            rank = base.groupby("country")["carat"].sum().sort_values(ascending=False)
        elif metric_choice == "USD per Carat":
            # weighted average across the selected period
            tmp = base.groupby("country", as_index=False)[["us_value", "carat"]].sum()
            tmp["metric"] = np.where(tmp["carat"] > 0, tmp["us_value"] / tmp["carat"], np.nan)
            rank = tmp.set_index("country")["metric"].sort_values(ascending=False)
        else:
            rank = base.groupby("country")["us_value"].sum().sort_values(ascending=False)

        top_countries = rank.head(int(top_n_data)).index.tolist()
        base = base[base["country"].isin(top_countries)].copy()

        # Build wide table (Years as columns)
        if metric_choice == "Carat":
            wide = base.pivot_table(index="country", columns="year", values="carat", aggfunc="sum")
            wide_label = "Carat"
        elif metric_choice == "Million Carats":
            wide = base.pivot_table(index="country", columns="year", values="carat", aggfunc="sum") / 1_000_000
            wide_label = "Million Carats"
        elif metric_choice == "USD per Carat":
            # per country-year: us_value sum / carat sum
            by = base.groupby(["country", "year"], as_index=False)[["us_value", "carat"]].sum()
            by["usd_per_carat"] = np.where(by["carat"] > 0, by["us_value"] / by["carat"], np.nan)
            wide = by.pivot_table(index="country", columns="year", values="usd_per_carat", aggfunc="mean")
            wide_label = "USD/Carat (USD)"
        else:
            base["us_value_disp"] = base["us_value"] / usd_div
            wide = base.pivot_table(index="country", columns="year", values="us_value_disp", aggfunc="sum")
            wide_label = f"US Value ({usd_unit_label})"

        wide = wide.sort_index(axis=1)
        wide = wide.loc[top_countries]  # keep rank order
        wide.insert(0, "Rank", range(1, len(wide) + 1))

        st.markdown(f"##### Top {len(top_countries)} countries — {wide_label} (Years as columns)")
        st.dataframe(wide.reset_index().rename(columns={"country": "Country"}), use_container_width=True, height=420)

        # YoY growth (wide)
        years_sorted = [c for c in wide.columns if isinstance(c, (int, np.integer)) or (isinstance(c, str) and str(c).isdigit())]
        # convert year columns to numeric for ordering
        year_cols = [c for c in wide.columns if c not in ["Rank"]]
        # only numeric year columns for yoy
        numeric_year_cols = [c for c in year_cols if isinstance(c, (int, np.integer))]
        yoy = wide[numeric_year_cols].copy()
        yoy = yoy.diff(axis=1) / yoy.shift(axis=1) * 100
        yoy.insert(0, "Rank", wide["Rank"])
        st.markdown("##### YoY growth (%) — Years as columns")
        st.dataframe(yoy.reset_index().rename(columns={"country": "Country"}), use_container_width=True, height=360)

        # Download buttons
        csv_level = wide.reset_index().rename(columns={"country": "Country"}).to_csv(index=False).encode("utf-8")
        csv_yoy = yoy.reset_index().rename(columns={"country": "Country"}).to_csv(index=False).encode("utf-8")

        d1, d2 = st.columns(2)
        with d1:
            st.download_button(
                "⬇️ Download level data (CSV)",
                data=csv_level,
                file_name=f"production_top{len(top_countries)}_{wide_label.replace('/', '_').replace(' ', '_')}_{start_year}-{end_year}.csv",
                mime="text/csv",
            )
        with d2:
            st.download_button(
                "⬇️ Download YoY growth (CSV)",
                data=csv_yoy,
                file_name=f"production_top{len(top_countries)}_yoy_{start_year}-{end_year}.csv",
                mime="text/csv",
            )

        # Optional: long-form filtered data preview
        st.markdown("##### Long-form (filtered) data preview")
        preview = base.copy()
        preview["us_value_disp"] = preview["us_value"] / usd_div
        preview = preview[["country", "year", "carat", "us_value_disp", "usd_per_carat"]].rename(
            columns={"country": "Country", "year": "Year", "us_value_disp": f"US Value ({usd_unit_label})", "usd_per_carat": "USD/Carat"}
        )
        st.dataframe(preview.sort_values(["Year", "Country"]), use_container_width=True, height=420)



# -----------------------------
# Trade (HS 7102) — Parsing helpers
# -----------------------------
TRADE_DEFAULTS = ["Diamonds(7102).xlsx"]

# Lab-grown diamonds (HS 7104) default workbook
LAB7104_DEFAULTS = [
    "Lab Grown Diamonds-7104.xlsx",
    "Lab Grown Diamonds 7104.xlsx",
    "Lab Grown Diamonds(7104).xlsx",
]

# HS6 -> (HS6, description) for Lab-grown
LAB7104_SHEETS: dict[str, tuple[str, str]] = {
    "710421": ("710421", "Lab-grown diamonds, unworked"),
    "710491": ("710491", "Lab-grown diamonds, worked"),
}


# HS6 -> (HS6, description)
TRADE_SHEETS: dict[str, tuple[str, str]] = {
    "710210": ("710210", "Diamonds, unsorted (ROUGH)"),
    "710221": ("710221", "Industrial diamonds, unworked, sorted (ROUGH)"),
    "710231": ("710231", "Non-industrial diamonds, unworked (ROUGH)"),
    "710229": ("710229", "Industrial diamonds, worked (CUT & POLISHED)"),
    "710239": ("710239", "Diamonds, worked, non-industrial (CUT & POLISHED)"),
}

ROUGH_UNSORTED = {"710210", "710231"}
ROUGH_SORTED = {"710221"}
CP_INDUSTRIAL = {"710229"}
CP_NON_INDUSTRIAL = {"710239"}


def _find_sheet_name(xls: pd.ExcelFile, hs6: str) -> str | None:
    """Match sheet by stripping spaces (your 710210 sheet has a trailing space)."""
    for sn in xls.sheet_names:
        if str(sn).strip() == hs6:
            return sn
    return None


def _find_sheet_contains(xls: pd.ExcelFile, token: str) -> str | None:
    """Find a sheet whose name contains the given token (case-insensitive)."""
    tok = str(token).strip().lower()
    for sn in xls.sheet_names:
        if tok in str(sn).strip().lower():
            return sn
    return None


def _extract_year_cols(header_row: list) -> tuple[list[int], list[int]]:
    """
    Detect year columns in HS6 sheets.

    The trade sheets typically have headers like:
      - "Imported value in 2005", "Imported value in 2006", ...
      - or numeric years (2005, 2006, ...)
    """
    years: list[int] = []
    col_idxs: list[int] = []
    for j, h in enumerate(header_row):
        if j == 0:
            continue
        if pd.isna(h):
            continue

        # Numeric year
        if isinstance(h, (int, np.integer)) and 1900 <= int(h) <= 2100:
            years.append(int(h))
            col_idxs.append(j)
            continue
        if isinstance(h, (float, np.floating)) and np.isfinite(h) and 1900 <= int(h) <= 2100 and float(h).is_integer():
            years.append(int(h))
            col_idxs.append(j)
            continue

        s = str(h)
        m = re.search(r"(19\d{2}|20\d{2})", s)  # NOTE: this is a *regex* escape, not a Python-string escape
        if m:
            years.append(int(m.group(1)))
            col_idxs.append(j)

    return years, col_idxs


def _parse_trade_block(
    df: pd.DataFrame,
    header_row_idx: int,
    end_row_idx_exclusive: int,
    flow: str
) -> pd.DataFrame:
    """
    Parse either the Imports block or Exports block from a HS6 sheet.

    Robustness: if the 'Importers/Exporters' row isn't the true header row,
    we try the next non-empty row as a fallback header.
    """
    header = df.iloc[header_row_idx].tolist()
    years, col_idxs = _extract_year_cols(header)

    # Fallback: sometimes the year columns are one row below
    if not years and header_row_idx + 1 < len(df):
        header2 = df.iloc[header_row_idx + 1].tolist()
        years2, col2 = _extract_year_cols(header2)
        if years2:
            header_row_idx = header_row_idx + 1
            years, col_idxs = years2, col2

    if not years:
        raise ValueError(f"Could not detect year columns for {flow}.")

    block = df.iloc[header_row_idx + 1 : end_row_idx_exclusive, [0] + col_idxs].copy()
    block.columns = ["country"] + [str(y) for y in years]
    block = block.dropna(subset=["country"])
    block["country"] = block["country"].astype(str).str.strip()

    long_df = block.melt(id_vars=["country"], var_name="year", value_name="value")
    long_df["year"] = pd.to_numeric(long_df["year"], errors="coerce").astype("Int64")
    long_df["value"] = pd.to_numeric(long_df["value"], errors="coerce")
    long_df["flow"] = flow
    long_df = long_df.dropna(subset=["year"])
    return long_df


def _parse_hs_sheet(xls: pd.ExcelFile, sheet_name: str, hs6: str, hs_desc: str) -> pd.DataFrame:
    df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
    col0 = df.iloc[:, 0].astype(str).str.strip()
    low = col0.str.lower()

    imp_row = low[low == "importers"].index[0]
    exp_row = low[low == "exporters"].index[0]

    # Imports: up to the row before the EXPORTS title row (typically exp_row-1)
    imp_long = _parse_trade_block(df, imp_row, exp_row - 1, flow="Imports")

    # Exports: until last valid country row
    exp_end = df.iloc[exp_row + 1 :, 0].last_valid_index()
    exp_long = _parse_trade_block(df, exp_row, exp_end + 1, flow="Exports")

    out = pd.concat([imp_long, exp_long], ignore_index=True)
    out["hs6"] = hs6
    out["hs_desc"] = hs_desc
    return out


def _attach_groups(df: pd.DataFrame) -> pd.DataFrame:
    def group(hs: str) -> str:
        if hs in ROUGH_UNSORTED or hs in ROUGH_SORTED:
            return "Rough Diamonds"
        return "Cut & Polished Diamonds"

    def subgroup(hs: str) -> str:
        if hs in ROUGH_UNSORTED:
            return "Unsorted"
        if hs in ROUGH_SORTED:
            return "Sorted"
        if hs in CP_INDUSTRIAL:
            return "Industrial"
        if hs in CP_NON_INDUSTRIAL:
            return "Non-Industrial"
        return "Other"

    df = df.copy()
    df["group"] = df["hs6"].astype(str).apply(group)
    df["subgroup"] = df["hs6"].astype(str).apply(subgroup)
    df["country"] = df["country"].astype(str).str.strip()
    return df


@st.cache_data(show_spinner=False)
def load_trade_7102_from_path(path: str) -> pd.DataFrame:
    xls = pd.ExcelFile(path)
    frames: list[pd.DataFrame] = []
    for hs6, (code, desc) in TRADE_SHEETS.items():
        sn = _find_sheet_name(xls, hs6)
        if sn is None:
            continue
        frames.append(_parse_hs_sheet(xls, sn, code, desc))
    if not frames:
        raise ValueError("No HS6 sheets were parsed. Check sheet names / file.")
    out = pd.concat(frames, ignore_index=True)
    out = _attach_groups(out)
    return out


@st.cache_data(show_spinner=False)
def load_trade_7102_from_bytes(file_bytes: bytes) -> pd.DataFrame:
    xls = pd.ExcelFile(file_bytes)
    frames: list[pd.DataFrame] = []
    for hs6, (code, desc) in TRADE_SHEETS.items():
        sn = _find_sheet_name(xls, hs6)
        if sn is None:
            continue
        frames.append(_parse_hs_sheet(xls, sn, code, desc))
    if not frames:
        raise ValueError("No HS6 sheets were parsed. Check sheet names / file.")
    out = pd.concat(frames, ignore_index=True)
    out = _attach_groups(out)
    return out



@st.cache_data(show_spinner=False)
def load_trade_7104_from_path(path: str) -> pd.DataFrame:
    """
    Load Lab-grown diamonds trade workbook (HS 7104) which contains two sheets:
      - 710421-UNWORKED (imports + exports blocks)
      - 710491-WORKED   (imports + exports blocks)

    Each sheet contains BOTH imports and exports, in the same TradeMap-style layout.
    """
    xls = pd.ExcelFile(path)
    frames: list[pd.DataFrame] = []
    for hs6, (code, desc) in LAB7104_SHEETS.items():
        sn = _find_sheet_contains(xls, hs6) or _find_sheet_name(xls, hs6)
        if sn is None:
            continue
        frames.append(_parse_hs_sheet(xls, sn, code, desc))
    if not frames:
        raise ValueError("No 7104 sheets were parsed. Check sheet names / file.")
    out = pd.concat(frames, ignore_index=True)
    out["group"] = "Lab Grown Diamonds"
    out["subgroup"] = np.where(out["hs6"].astype(str) == "710421", "Unworked", "Worked")
    out["country"] = out["country"].astype(str).str.strip()
    return out



def _usd_scale_choice_trade(key_prefix: str) -> tuple[str, float]:
    """
    Trade 'value' fields in the HS 7102 / 7104 workbooks are **USD thousand (TradeMap style)**.
    This returns (label, divisor) for DISPLAY ONLY:
      - USD Mn: divide by 1e3
      - USD Bn: divide by 1e6
    """
    scale = st.radio(
        "Value display unit (Trade — scaling only)",
        ["USD thousand (as in file)", "USD Mn", "USD Bn"],
        index=1,
        horizontal=True,
        key=f"{key_prefix}_usd_scale_main",
    )
    if scale == "USD Mn":
        return "USD Mn", 1e3
    if scale == "USD Bn":
        return "USD Bn", 1e6
    return "USD thousand", 1.0


def _top_n_plus_others_trade(
    base: pd.DataFrame,
    *,
    flow: str,
    snap_year: int,
    top_n: int,
    metric: str,
    world: pd.DataFrame,
    usd_div: float,
    usd_label: str,
) -> tuple[pd.DataFrame, str]:
    """Build Top N + Others table for snapshot partner ranking.

    Returns (snapshot_df, metric_title).
    snapshot_df columns: country, metric_val, rank, metric_disp
    """
    snap = base[(base["flow"] == flow) & (base["year"] == snap_year)].copy()
    if snap.empty:
        return pd.DataFrame(columns=["country", "metric_val", "rank", "metric_disp"]), ""

    snap = snap.groupby(["country"], as_index=False)["value"].sum()
    snap = snap[snap["country"].astype(str).str.lower() != "world"].copy()
    if snap.empty:
        return pd.DataFrame(columns=["country", "metric_val", "rank", "metric_disp"]), ""

    world_total = float(world.loc[world["year"] == snap_year, flow].iloc[0]) if not world.empty else np.nan

    if metric == "Value":
        snap["metric_val"] = snap["value"] / usd_div
        metric_title = f"Value ({usd_label})"
        text_fmt = lambda v: f"{v:,.2f}"
    else:
        snap["metric_val"] = np.where(world_total > 0, (snap["value"] / world_total) * 100.0, np.nan)
        metric_title = "Share of world (%)"
        text_fmt = lambda v: f"{v:,.2f}%"

    snap = snap.sort_values("metric_val", ascending=False).reset_index(drop=True)
    top = snap.head(top_n).copy()
    rest = snap.iloc[top_n:].copy()

    others_value = float(rest["value"].sum()) if not rest.empty else 0.0
    if others_value > 0:
        if metric == "Value":
            others_metric = others_value / usd_div
        else:
            others_metric = (others_value / world_total) * 100.0 if world_total and world_total > 0 else np.nan

        top = pd.concat(
            [
                top,
                pd.DataFrame(
                    {
                        "country": ["Others"],
                        "value": [others_value],
                        "metric_val": [others_metric],
                    }
                ),
            ],
            ignore_index=True,
        )

    top["rank"] = np.arange(1, len(top) + 1)
    top["metric_disp"] = top["metric_val"].apply(lambda x: text_fmt(x) if np.isfinite(x) else "NA")
    return top[["country", "metric_val", "rank", "metric_disp"]].copy(), metric_title

def _render_trade_group_module(
    title: str,
    group_name: str,
    category_hs6_map: dict[str, set[str]] | list[str],
    sidebar_key_prefix: str,
) -> None:
    """Shared renderer for Rough Diamonds and Cut & Polished Diamonds (HS 7102)."""

    # --- File ---
    default_path = pick_first_existing(["Diamonds(7102).xlsx", "Diamonds (7102).xlsx"])
    trade_df = load_trade_7102_from_path(default_path) if default_path else pd.DataFrame()

    render_hero_header(
        title=title,
        subtitle="Trade (HS 7102) • ITC Trade Map • base data: USD thousand • scaling affects display only",
        badge="2005–2024",
        icon="💎",
    )

    if trade_df.empty:
        st.error("Could not load the HS 7102 trade file. Please ensure the Excel file is present.")
        return

    st.caption(f"File loaded: {Path(default_path).name}")

    # --- Sidebar filters ---
    st.sidebar.markdown("### Trade filters")

    y_min = int(trade_df["year"].min())
    y_max = int(trade_df["year"].max())
    year_lo, year_hi = st.sidebar.slider(
        "Year range",
        min_value=y_min,
        max_value=y_max,
        value=(y_min, y_max),
        step=1,
        key=f"{sidebar_key_prefix}_year_range",
    )

    ranking_flow = st.sidebar.selectbox(
        "Partner ranking based on",
        ["Exports", "Imports"],
        index=0,
        key=f"{sidebar_key_prefix}_flow",
    )

    # Category filter:
    # - For HS 7102 modules we pass a mapping of friendly labels -> HS6 code set.
    # - We keep a small fallback for older list-based usage.
    if isinstance(category_hs6_map, dict):
        cat_labels = list(category_hs6_map.keys())
        default_labels = [cat_labels[0]] if cat_labels else []
        cat_sel = st.sidebar.multiselect(
            "Category",
            options=cat_labels,
            default=default_labels,
            key=f"{sidebar_key_prefix}_category",
        )
        hs6_allowed: set[str] = set()
        for lab in cat_sel:
            hs6_allowed |= set(category_hs6_map.get(lab, set()))
        if not hs6_allowed:
            # If user clears the selection, revert to ALL HS6 codes in the map.
            for s in category_hs6_map.values():
                hs6_allowed |= set(s)
    else:
        # Backward-compatible: treat list values as subgroup labels.
        subgroup_options = list(category_hs6_map)
        subgroup_sel = st.sidebar.multiselect(
            "Category",
            options=subgroup_options,
            default=subgroup_options,
            key=f"{sidebar_key_prefix}_subgroup",
        )
        hs6_allowed = set(trade_df.loc[trade_df["subgroup"].isin(subgroup_sel), "hs6"].astype(str).tolist())

    metric = st.sidebar.radio(
        "Metric",
        ["Value", "Share of world (%)"],
        index=0,
        key=f"{sidebar_key_prefix}_metric",
        horizontal=False,
    )

    # --- Display unit (main area, like your Gold dashboard) ---
    st.markdown("#### Display unit")
    st.caption("Trade values are stored as USD thousand in the source file. Scaling affects display only.")
    usd_label, usd_div = _usd_scale_choice_trade(f"{sidebar_key_prefix}_unit")

    show_labels = bool(st.session_state.get("show_data_labels", False))

    # --- Filter base (keep BOTH flows for KPIs + global trend) ---
    if not hs6_allowed:
        hs6_allowed = set(trade_df.loc[trade_df["group"] == group_name, "hs6"].astype(str).unique().tolist())

    base = trade_df[
        (trade_df["group"] == group_name)
        & (trade_df["hs6"].astype(str).isin(hs6_allowed))
        & (trade_df["year"].between(year_lo, year_hi))
    ].copy()

    if base.empty:
        st.warning("No trade records match the selected filters.")
        return

    # --- Helpers ---
    def _world_series(df: pd.DataFrame) -> pd.DataFrame:
        w = df[df["country"].astype(str).str.lower() == "world"]
        if w.empty:
            w = df[df["country"].astype(str).str.lower() != "world"].groupby(["year", "flow"], as_index=False)["value"].sum()
        else:
            w = w.groupby(["year", "flow"], as_index=False)["value"].sum()

        p = w.pivot(index="year", columns="flow", values="value").fillna(0.0)
        for col in ["Exports", "Imports"]:
            if col not in p.columns:
                p[col] = 0.0
        p = p.reset_index().sort_values("year")
        p["Trade Balance"] = p["Exports"] - p["Imports"]
        return p

    world = _world_series(base)

    # Years available for snapshot selection
    years = world["year"].tolist()
    snap_year_default = years[-1] if years else year_hi

    # --- Snapshot defaults (persist across tabs) ---
    snap_key = f"{sidebar_key_prefix}_snap_year"
    topn_key = f"{sidebar_key_prefix}_topn"
    if snap_key not in st.session_state or st.session_state.get(snap_key) not in years:
        st.session_state[snap_key] = snap_year_default
    if topn_key not in st.session_state:
        st.session_state[topn_key] = 10

    # --- Tabs ---
    tab_overview, tab_topn, tab_country, tab_data = st.tabs(["📌 Overview", "🌍 Top N countries", "📈 Country trend", "⬇️ Download"])

    # -----------------------------
    # Overview
    # -----------------------------
    with tab_overview:
        snap_year = int(st.session_state.get(snap_key, snap_year_default))

        # --- KPI cards (World totals) ---
        row = world[world["year"] == snap_year]
        prev = world[world["year"] == (snap_year - 1)]

        exp = float(row["Exports"].iloc[0]) if not row.empty else 0.0
        imp = float(row["Imports"].iloc[0]) if not row.empty else 0.0
        bal = exp - imp

        exp_prev = float(prev["Exports"].iloc[0]) if not prev.empty else np.nan
        imp_prev = float(prev["Imports"].iloc[0]) if not prev.empty else np.nan

        exp_yoy = (exp - exp_prev) / exp_prev * 100 if exp_prev and exp_prev > 0 else np.nan
        imp_yoy = (imp - imp_prev) / imp_prev * 100 if imp_prev and imp_prev > 0 else np.nan

        # CAGR across selected range
        first_year = int(world["year"].min())
        last_year = int(world["year"].max())
        n_years = max(last_year - first_year, 0)

        exp_start = float(world.loc[world["year"] == first_year, "Exports"].iloc[0]) if not world.empty else np.nan
        exp_end = float(world.loc[world["year"] == last_year, "Exports"].iloc[0]) if not world.empty else np.nan
        imp_start = float(world.loc[world["year"] == first_year, "Imports"].iloc[0]) if not world.empty else np.nan
        imp_end = float(world.loc[world["year"] == last_year, "Imports"].iloc[0]) if not world.empty else np.nan

        exp_cagr = ((exp_end / exp_start) ** (1 / n_years) - 1) * 100 if n_years and exp_start and exp_start > 0 else np.nan
        imp_cagr = ((imp_end / imp_start) ** (1 / n_years) - 1) * 100 if n_years and imp_start and imp_start > 0 else np.nan

        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            st.metric(
                f"Exports ({snap_year})",
                f"{exp / usd_div:,.2f} {usd_label}",
                delta=(f"{exp_yoy:+.1f}% YoY" if np.isfinite(exp_yoy) else None),
            )
        with k2:
            st.metric(
                f"Imports ({snap_year})",
                f"{imp / usd_div:,.2f} {usd_label}",
                delta=(f"{imp_yoy:+.1f}% YoY" if np.isfinite(imp_yoy) else None),
            )
        with k3:
            st.metric(
                f"Trade balance ({snap_year})",
                f"{bal / usd_div:,.2f} {usd_label}",
                delta=("Surplus" if bal >= 0 else "Deficit"),
            )
        with k4:
            st.metric(
                f"CAGR Exports ({first_year}–{last_year})",
                f"{exp_cagr:+.1f}%" if np.isfinite(exp_cagr) else "NA",
            )
        with k5:
            st.metric(
                f"CAGR Imports ({first_year}–{last_year})",
                f"{imp_cagr:+.1f}%" if np.isfinite(imp_cagr) else "NA",
            )

        # --- Global trade trend chart ---
        trend = world.copy()
        trend["Exports_disp"] = trend["Exports"] / usd_div
        trend["Imports_disp"] = trend["Imports"] / usd_div
        trend["Balance_disp"] = trend["Trade Balance"] / usd_div

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(
                x=trend["year"],
                y=trend["Exports_disp"],
                name="Exports",
                mode="lines+markers" + ("+text" if show_labels else ""),
                text=[f"{v:,.2f}" for v in trend["Exports_disp"]] if show_labels else None,
                textposition="top center",
                line=dict(color="#0b6ea8", width=3),
                marker=dict(size=7, color="#0b6ea8"),
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=trend["year"],
                y=trend["Imports_disp"],
                name="Imports",
                mode="lines+markers" + ("+text" if show_labels else ""),
                text=[f"{v:,.2f}" for v in trend["Imports_disp"]] if show_labels else None,
                textposition="top center",
                line=dict(color="#5aa7d6", width=3),
                marker=dict(size=7, color="#5aa7d6"),
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=trend["year"],
                y=trend["Balance_disp"],
                name="Trade balance",
                mode="lines",
                line=dict(color="rgba(90,107,130,0.75)", width=2, dash="dot"),
            ),
            secondary_y=True,
        )
        fig.update_layout(
            title=f"Global trade trend ({usd_label})",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig.update_xaxes(title_text="Year")
        fig.update_yaxes(title_text=usd_label, secondary_y=False)
        fig.update_yaxes(title_text="Balance", secondary_y=True)
        style_plotly(fig)
        st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Top N countries (snapshot)
    # -----------------------------
    with tab_topn:
        c1, c2 = st.columns([2, 3])
        with c1:
            snap_year = st.selectbox(
                "Snapshot year",
                options=years,
                index=years.index(int(st.session_state.get(snap_key, snap_year_default))) if years else 0,
                key=snap_key,
            )
        with c2:
            top_n = st.slider(
                "Top N countries (snapshot)",
                min_value=3,
                max_value=30,
                value=int(st.session_state.get(topn_key, 10)),
                step=1,
                key=topn_key,
            )

        snap_df, metric_title = _top_n_plus_others_trade(
            base,
            flow=ranking_flow,
            snap_year=int(snap_year),
            top_n=int(top_n),
            metric=metric,
            world=world,
            usd_div=usd_div,
            usd_label=usd_label,
        )

        if snap_df.empty or not metric_title:
            st.info("No snapshot data available for the selected year.")
        else:
            plot_df = snap_df.sort_values("metric_val", ascending=True)
            fig_bar = px.bar(
                plot_df,
                x="metric_val",
                y="country",
                orientation="h",
                text=("metric_disp" if show_labels else None),
                title=f"Top {min(int(top_n), max(len(snap_df) - (1 if (snap_df['country'] == 'Others').any() else 0), 0))} partners + Others — {ranking_flow} ({snap_year})",
            )
            fig_bar.update_traces(marker_color="#0b6ea8", textposition="outside")
            fig_bar.update_layout(xaxis_title=metric_title, yaxis_title="Country")
            fig_bar.update_yaxes(categoryorder="array", categoryarray=plot_df["country"].tolist())
            style_plotly(fig_bar)
            st.plotly_chart(fig_bar, use_container_width=True)

            st.subheader("Snapshot table (Top N + Others)")
            view = snap_df[["rank", "country", "metric_val"]].rename(columns={"country": "Partner", "metric_val": metric_title})

            # Add TOTAL row (Top N + Others + Total)
            total_val = float(view[metric_title].sum()) if not view.empty else 0.0
            total_row = pd.DataFrame({"rank": [""], "Partner": ["Total"], metric_title: [total_val]})
            view_total = pd.concat([view, total_row], ignore_index=True)

            def _bold_total_row(row):
                return ["font-weight: 800;"] * len(row) if str(row.get("Partner", "")) == "Total" else [""] * len(row)

            # Display formatting: avoid extra trailing zeros in the snapshot table
            view_total_out = view_total.copy()
            if metric_title in view_total_out.columns:
                view_total_out[metric_title] = pd.to_numeric(view_total_out[metric_title], errors="coerce").round(2)

            st.dataframe(
                view_total_out.style
                .apply(_bold_total_row, axis=1)
                .format({metric_title: "{:,.2f}"}),
                use_container_width=True,
            )

            csv = view_total_out.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download snapshot (CSV)",
                data=csv,
                file_name=f"{group_name}_{ranking_flow}_{int(snap_year)}_top{int(top_n)}_plus_others.csv",
                mime="text/csv",
                key=f"{sidebar_key_prefix}_dl_snap",
            )

    # -----------------------------
    # Country trend
    # -----------------------------
    with tab_country:
        partners = sorted(
            base[base["country"].astype(str).str.lower() != "world"]["country"].unique().tolist()
        )

        default_sel = partners[:5] if len(partners) >= 5 else partners
        sel = st.multiselect(
            "Select countries",
            partners,
            default=default_sel,
            key=f"{sidebar_key_prefix}_countries_multi",
        )
        include_world = st.checkbox("Include World", value=False, key=f"{sidebar_key_prefix}_include_world")
        if include_world:
            sel = ["World"] + [c for c in sel if c != "World"]

        if not sel:
            st.info("Select at least one country to see the trend.")
        else:
            d = base[(base["flow"] == ranking_flow) & (base["country"].isin(sel))].copy()
            d = d.groupby(["year", "country"], as_index=False)["value"].sum()
            if metric == "Value":
                d["y"] = d["value"] / usd_div
                y_title = f"Value ({usd_label})"
            else:
                totals = world.set_index("year")[ranking_flow].to_dict()
                d["y"] = d.apply(
                    lambda r: (r["value"] / totals.get(r["year"], np.nan) * 100.0) if totals.get(r["year"], 0) else np.nan,
                    axis=1,
                )
                d.loc[d["country"].astype(str).str.lower() == "world", "y"] = 100.0
                y_title = "Share of world (%)"

            fig_line = px.line(
                d.sort_values("year"),
                x="year",
                y="y",
                color="country",
                markers=True,
                text=("y" if show_labels else None),
                title=f"Country trend — {ranking_flow}",
            )
            if show_labels:
                fig_line.update_traces(textposition="top center")
            fig_line.update_layout(xaxis_title="Year", yaxis_title=y_title)
            style_plotly(fig_line)
            st.plotly_chart(fig_line, use_container_width=True)

            st.dataframe(d.pivot(index="country", columns="year", values="y").reset_index(), use_container_width=True)

    # -----------------------------
    # Download
    # -----------------------------
    with tab_data:
        st.markdown("### Downloadable table (years as columns)")
        top_n_dl = st.slider(
            "Top N countries (by total over selected years)",
            min_value=5,
            max_value=50,
            value=20,
            step=1,
            key=f"{sidebar_key_prefix}_topn_dl",
        )

        dl = base[base["flow"] == ranking_flow].copy()
        dl = dl[dl["country"].astype(str).str.lower() != "world"]
        dl = dl.groupby(["country", "year"], as_index=False)["value"].sum()

        totals = dl.groupby("country", as_index=False)["value"].sum().sort_values("value", ascending=False).head(top_n_dl)
        dl = dl[dl["country"].isin(totals["country"])].copy()

        if metric == "Value":
            dl["val"] = dl["value"] / usd_div
            wide = dl.pivot(index="country", columns="year", values="val").fillna(0.0)
            wide.index.name = "Country"
            wide_reset = wide.reset_index()
            st.dataframe(wide_reset, use_container_width=True)

            csv = wide_reset.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download values (CSV)",
                data=csv,
                file_name=f"{group_name}_{ranking_flow}_values_{year_lo}-{year_hi}_top{top_n_dl}.csv",
                mime="text/csv",
                key=f"{sidebar_key_prefix}_dl_values",
            )

            yoy = wide.pct_change(axis=1) * 100.0
            yoy_reset = yoy.reset_index()
            st.markdown("### YoY growth (%)")
            st.dataframe(yoy_reset, use_container_width=True)

            csv2 = yoy_reset.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download YoY growth (CSV)",
                data=csv2,
                file_name=f"{group_name}_{ranking_flow}_yoy_{year_lo}-{year_hi}_top{top_n_dl}.csv",
                mime="text/csv",
                key=f"{sidebar_key_prefix}_dl_yoy",
            )
        else:
            st.info("For Share of world (%), please use the Overview or Country trend tabs (share is computed relative to World totals).")


# -----------------------------
# Trade modules (new structure)
# -----------------------------
def render_rough_diamonds_module() -> None:
    category_hs6_map = {
        "All Rough (710210 + 710221 + 710231)": {"710210", "710221", "710231"},
        "Unsorted Rough (710210 + 710231)": {"710210", "710231"},
        "Sorted Rough (710221)": {"710221"},
    }
    _render_trade_group_module(
        title="Rough Diamonds",
        group_name="Rough Diamonds",
        category_hs6_map=category_hs6_map,
        sidebar_key_prefix="rough",
    )


def render_cut_polished_module() -> None:
    category_hs6_map = {
        "All Cut & Polished (710229 + 710239)": {"710229", "710239"},
        "Industrial (710229)": {"710229"},
        "Non-industrial (710239)": {"710239"},
    }
    _render_trade_group_module(
        title="Cut & Polished Diamonds",
        group_name="Cut & Polished Diamonds",
        category_hs6_map=category_hs6_map,
        sidebar_key_prefix="cp",
    )



def render_lab_grown_module() -> None:
    """Trade module for Lab Grown Diamonds (HS 7104)."""

    default_path = pick_first_existing(["Lab Grown Diamonds-7104.xlsx", "Lab Grown Diamonds - 7104.xlsx"])
    trade_df = load_trade_7104_from_path(default_path) if default_path else pd.DataFrame()

    render_hero_header(
        title="Lab Grown Diamonds",
        subtitle="Trade (HS 7104) • ITC Trade Map • base data: USD thousand • scaling affects display only",
        badge="2005–2024",
        icon="💎",
    )

    if trade_df.empty:
        st.error("Could not load the HS 7104 trade file. Please ensure the Excel file is present.")
        return

    st.caption(f"File loaded: {Path(default_path).name}")

    st.sidebar.markdown("### Trade filters")

    y_min = int(trade_df["year"].min())
    y_max = int(trade_df["year"].max())
    year_lo, year_hi = st.sidebar.slider(
        "Year range",
        min_value=y_min,
        max_value=y_max,
        value=(y_min, y_max),
        step=1,
        key="lg_year_range",
    )

    ranking_flow = st.sidebar.selectbox(
        "Partner ranking based on",
        ["Exports", "Imports"],
        index=0,
        key="lg_flow",
    )

    hs_options = trade_df[["hs6", "hs_desc"]].dropna().drop_duplicates()
    hs_options["label"] = hs_options["hs6"] + " — " + hs_options["hs_desc"]

    selected_hs = st.sidebar.multiselect(
        "Select product (HS6)",
        options=hs_options["label"].tolist(),
        default=hs_options["label"].tolist(),
        key="lg_hs_sel",
    )

    metric = st.sidebar.radio(
        "Metric",
        ["Value", "Share of world (%)"],
        index=0,
        key="lg_metric",
    )

    st.markdown("#### Display unit")
    st.caption("Trade values are stored as USD thousand in the source file. Scaling affects display only.")
    usd_label, usd_div = _usd_scale_choice_trade("lg_unit")

    show_labels = bool(st.session_state.get("show_data_labels", False))

    hs_selected = hs_options.loc[hs_options["label"].isin(selected_hs), "hs6"].tolist()
    base = trade_df[
        (trade_df["hs6"].isin(hs_selected))
        & (trade_df["year"].between(year_lo, year_hi))
    ].copy()

    if base.empty:
        st.warning("No trade records match the selected filters.")
        return

    def _world_series(df: pd.DataFrame) -> pd.DataFrame:
        w = df[df["country"].astype(str).str.lower() == "world"]
        if w.empty:
            w = df[df["country"].astype(str).str.lower() != "world"].groupby(["year", "flow"], as_index=False)["value"].sum()
        else:
            w = w.groupby(["year", "flow"], as_index=False)["value"].sum()

        p = w.pivot(index="year", columns="flow", values="value").fillna(0.0)
        for col in ["Exports", "Imports"]:
            if col not in p.columns:
                p[col] = 0.0
        p = p.reset_index().sort_values("year")
        p["Trade Balance"] = p["Exports"] - p["Imports"]
        return p

    world = _world_series(base)
    years = world["year"].tolist()
    snap_year_default = years[-1] if years else year_hi

    # --- Snapshot defaults (persist across tabs) ---
    snap_key = "lg_snap_year"
    topn_key = "lg_topn"
    if snap_key not in st.session_state or st.session_state.get(snap_key) not in years:
        st.session_state[snap_key] = snap_year_default
    if topn_key not in st.session_state:
        st.session_state[topn_key] = 10

    tab_overview, tab_topn, tab_country, tab_data = st.tabs(["📌 Overview", "🌍 Top N countries", "📈 Country trend", "⬇️ Download"])

    with tab_overview:
        snap_year = int(st.session_state.get(snap_key, snap_year_default))

        row = world[world["year"] == snap_year]
        prev = world[world["year"] == (snap_year - 1)]

        exp = float(row["Exports"].iloc[0]) if not row.empty else 0.0
        imp = float(row["Imports"].iloc[0]) if not row.empty else 0.0
        bal = exp - imp

        exp_prev = float(prev["Exports"].iloc[0]) if not prev.empty else np.nan
        imp_prev = float(prev["Imports"].iloc[0]) if not prev.empty else np.nan

        exp_yoy = (exp - exp_prev) / exp_prev * 100 if exp_prev and exp_prev > 0 else np.nan
        imp_yoy = (imp - imp_prev) / imp_prev * 100 if imp_prev and imp_prev > 0 else np.nan

        first_year = int(world["year"].min())
        last_year = int(world["year"].max())
        n_years = max(last_year - first_year, 0)

        exp_start = float(world.loc[world["year"] == first_year, "Exports"].iloc[0]) if not world.empty else np.nan
        exp_end = float(world.loc[world["year"] == last_year, "Exports"].iloc[0]) if not world.empty else np.nan
        imp_start = float(world.loc[world["year"] == first_year, "Imports"].iloc[0]) if not world.empty else np.nan
        imp_end = float(world.loc[world["year"] == last_year, "Imports"].iloc[0]) if not world.empty else np.nan

        exp_cagr = ((exp_end / exp_start) ** (1 / n_years) - 1) * 100 if n_years and exp_start and exp_start > 0 else np.nan
        imp_cagr = ((imp_end / imp_start) ** (1 / n_years) - 1) * 100 if n_years and imp_start and imp_start > 0 else np.nan

        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            st.metric(
                f"Exports ({snap_year})",
                f"{exp / usd_div:,.2f} {usd_label}",
                delta=(f"{exp_yoy:+.1f}% YoY" if np.isfinite(exp_yoy) else None),
            )
        with k2:
            st.metric(
                f"Imports ({snap_year})",
                f"{imp / usd_div:,.2f} {usd_label}",
                delta=(f"{imp_yoy:+.1f}% YoY" if np.isfinite(imp_yoy) else None),
            )
        with k3:
            st.metric(
                f"Trade balance ({snap_year})",
                f"{bal / usd_div:,.2f} {usd_label}",
                delta=("Surplus" if bal >= 0 else "Deficit"),
            )
        with k4:
            st.metric(
                f"CAGR Exports ({first_year}–{last_year})",
                f"{exp_cagr:+.1f}%" if np.isfinite(exp_cagr) else "NA",
            )
        with k5:
            st.metric(
                f"CAGR Imports ({first_year}–{last_year})",
                f"{imp_cagr:+.1f}%" if np.isfinite(imp_cagr) else "NA",
            )

        trend = world.copy()
        trend["Exports_disp"] = trend["Exports"] / usd_div
        trend["Imports_disp"] = trend["Imports"] / usd_div
        trend["Balance_disp"] = trend["Trade Balance"] / usd_div

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(
                x=trend["year"],
                y=trend["Exports_disp"],
                name="Exports",
                mode="lines+markers" + ("+text" if show_labels else ""),
                text=[f"{v:,.2f}" for v in trend["Exports_disp"]] if show_labels else None,
                textposition="top center",
                line=dict(color="#0b6ea8", width=3),
                marker=dict(size=7, color="#0b6ea8"),
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=trend["year"],
                y=trend["Imports_disp"],
                name="Imports",
                mode="lines+markers" + ("+text" if show_labels else ""),
                text=[f"{v:,.2f}" for v in trend["Imports_disp"]] if show_labels else None,
                textposition="top center",
                line=dict(color="#5aa7d6", width=3),
                marker=dict(size=7, color="#5aa7d6"),
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=trend["year"],
                y=trend["Balance_disp"],
                name="Trade balance",
                mode="lines",
                line=dict(color="rgba(90,107,130,0.75)", width=2, dash="dot"),
            ),
            secondary_y=True,
        )
        fig.update_layout(
            title=f"Global trade trend ({usd_label})",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig.update_xaxes(title_text="Year")
        fig.update_yaxes(title_text=usd_label, secondary_y=False)
        fig.update_yaxes(title_text="Balance", secondary_y=True)
        style_plotly(fig)
        st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Top N countries (snapshot)
    # -----------------------------
    with tab_topn:
        c1, c2 = st.columns([2, 3])
        with c1:
            snap_year = st.selectbox(
                "Snapshot year",
                options=years,
                index=years.index(int(st.session_state.get(snap_key, snap_year_default))) if years else 0,
                key=snap_key,
            )
        with c2:
            top_n = st.slider(
                "Top N countries (snapshot)",
                min_value=3,
                max_value=30,
                value=int(st.session_state.get(topn_key, 10)),
                step=1,
                key=topn_key,
            )

        snap_df, metric_title = _top_n_plus_others_trade(
            base,
            flow=ranking_flow,
            snap_year=int(snap_year),
            top_n=int(top_n),
            metric=metric,
            world=world,
            usd_div=usd_div,
            usd_label=usd_label,
        )

        if snap_df.empty or not metric_title:
            st.info("No snapshot data available for the selected year.")
        else:
            plot_df = snap_df.sort_values("metric_val", ascending=True)
            fig_bar = px.bar(
                plot_df,
                x="metric_val",
                y="country",
                orientation="h",
                text=("metric_disp" if show_labels else None),
                title=f"Top {min(int(top_n), max(len(snap_df) - (1 if (snap_df['country'] == 'Others').any() else 0), 0))} partners + Others — {ranking_flow} ({snap_year})",
            )
            fig_bar.update_traces(marker_color="#0b6ea8", textposition="outside")
            fig_bar.update_layout(xaxis_title=metric_title, yaxis_title="Country")
            fig_bar.update_yaxes(categoryorder="array", categoryarray=plot_df["country"].tolist())
            style_plotly(fig_bar)
            st.plotly_chart(fig_bar, use_container_width=True)

            st.subheader("Snapshot table (Top N + Others)")
            view = snap_df[["rank", "country", "metric_val"]].rename(columns={"country": "Partner", "metric_val": metric_title})

            # Add TOTAL row (Top N + Others + Total)
            total_val = float(view[metric_title].sum()) if not view.empty else 0.0
            total_row = pd.DataFrame({"rank": [""], "Partner": ["Total"], metric_title: [total_val]})
            view_total = pd.concat([view, total_row], ignore_index=True)

            def _bold_total_row(row):
                return ["font-weight: 800;"] * len(row) if str(row.get("Partner", "")) == "Total" else [""] * len(row)

            # Display formatting: avoid extra trailing zeros in the snapshot table
            view_total_out = view_total.copy()
            if metric_title in view_total_out.columns:
                view_total_out[metric_title] = pd.to_numeric(view_total_out[metric_title], errors="coerce").round(2)

            st.dataframe(
                view_total_out.style.apply(_bold_total_row, axis=1).format({metric_title: "{:,.2f}"}),
                use_container_width=True,
            )

            csv = view_total_out.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download snapshot (CSV)",
                data=csv,
                file_name=f"7104_{ranking_flow}_{int(snap_year)}_top{int(top_n)}_plus_others.csv",
                mime="text/csv",
                key="lg_dl_snap",
            )

    with tab_country:
        partners = sorted(base[base["country"].astype(str).str.lower() != "world"]["country"].unique().tolist())
        default_sel = partners[:5] if len(partners) >= 5 else partners
        sel = st.multiselect("Select countries", partners, default=default_sel, key="lg_countries_multi")
        include_world = st.checkbox("Include World", value=False, key="lg_include_world")
        if include_world:
            sel = ["World"] + [c for c in sel if c != "World"]

        if not sel:
            st.info("Select at least one country to see the trend.")
        else:
            d = base[(base["flow"] == ranking_flow) & (base["country"].isin(sel))].copy()
            d = d.groupby(["year", "country"], as_index=False)["value"].sum()

            if metric == "Value":
                d["y"] = d["value"] / usd_div
                y_title = f"Value ({usd_label})"
            else:
                totals = world.set_index("year")[ranking_flow].to_dict()
                d["y"] = d.apply(lambda r: (r["value"] / totals.get(r["year"], np.nan) * 100.0) if totals.get(r["year"], 0) else np.nan, axis=1)
                d.loc[d["country"].astype(str).str.lower() == "world", "y"] = 100.0
                y_title = "Share of world (%)"

            fig_line = px.line(
                d.sort_values("year"),
                x="year",
                y="y",
                color="country",
                markers=True,
                text=("y" if show_labels else None),
                title=f"Country trend — {ranking_flow}",
            )
            if show_labels:
                fig_line.update_traces(textposition="top center")
            fig_line.update_layout(xaxis_title="Year", yaxis_title=y_title)
            style_plotly(fig_line)
            st.plotly_chart(fig_line, use_container_width=True)

            st.dataframe(d.pivot(index="country", columns="year", values="y").reset_index(), use_container_width=True)

    with tab_data:
        st.markdown("### Downloadable table (years as columns)")
        top_n_dl = st.slider("Top N countries (by total over selected years)", 5, 50, 20, 1, key="lg_topn_dl")

        dl = base[base["flow"] == ranking_flow].copy()
        dl = dl[dl["country"].astype(str).str.lower() != "world"]
        dl = dl.groupby(["country", "year"], as_index=False)["value"].sum()

        totals = dl.groupby("country", as_index=False)["value"].sum().sort_values("value", ascending=False).head(top_n_dl)
        dl = dl[dl["country"].isin(totals["country"])].copy()

        if metric == "Value":
            dl["val"] = dl["value"] / usd_div
            wide = dl.pivot(index="country", columns="year", values="val").fillna(0.0)
            wide.index.name = "Country"
            wide_reset = wide.reset_index()
            st.dataframe(wide_reset, use_container_width=True)

            csv = wide_reset.to_csv(index=False).encode("utf-8")
            st.download_button("Download values (CSV)", data=csv, file_name=f"7104_{ranking_flow}_values_{year_lo}-{year_hi}_top{top_n_dl}.csv", mime="text/csv", key="lg_dl_values")

            yoy = wide.pct_change(axis=1) * 100.0
            yoy_reset = yoy.reset_index()
            st.markdown("### YoY growth (%)")
            st.dataframe(yoy_reset, use_container_width=True)

            csv2 = yoy_reset.to_csv(index=False).encode("utf-8")
            st.download_button("Download YoY growth (CSV)", data=csv2, file_name=f"7104_{ranking_flow}_yoy_{year_lo}-{year_hi}_top{top_n_dl}.csv", mime="text/csv", key="lg_dl_yoy")
        else:
            st.info("For Share of world (%), please use the Overview or Country trend tabs (share is computed relative to World totals).")


def main() -> None:
    st.set_page_config(page_title="Diamonds - Production + Trade Intelligence", layout="wide")
    apply_theme()

    # KPI auto-font (visual-only): keep metrics readable across screen sizes
    st.markdown(
        """
<style>
div[data-testid="stMetricLabel"] > div {
  font-size: clamp(0.72rem, 0.85vw, 0.98rem) !important;
  line-height: 1.15 !important;
  white-space: normal !important;
  overflow-wrap: anywhere !important;
}
div[data-testid="stMetricValue"] > div {
  font-size: clamp(1.05rem, 1.65vw, 1.85rem) !important;
  line-height: 1.10 !important;
  white-space: normal !important;
  overflow-wrap: anywhere !important;
}
</style>
""",
        unsafe_allow_html=True,
    )

    st.sidebar.header("DIAMONDS💎•HS 7102 •HS 7104")
    module = st.sidebar.radio(
        "Choose module",
        ["Production (Diamonds)", "Rough Diamonds (Trade 7102)", "Cut & Polished Diamonds (Trade 7102)", "Lab Grown Diamonds (Trade 7104)"],
        index=0,
        key="module",
    )

    # Global visual toggle
    st.sidebar.checkbox("Show data labels", value=False, key="show_data_labels")

    if module == "Production (Diamonds)":
        render_production_module()
    elif module == "Rough Diamonds (Trade 7102)":
        render_rough_diamonds_module()
    elif module == "Cut & Polished Diamonds (Trade 7102)":
        render_cut_polished_module()
    else:
        render_lab_grown_module()


if __name__ == "__main__":
    main()
