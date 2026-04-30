import streamlit as st
import pandas as pd
import numpy as np
import math
import yfinance as yf
import datetime as dt
from functions import calc_moving_average, calc_macd, RSI, ADX, is_breaking_out, is_consolidating
from millify import millify

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Screener Pro", layout="wide")

# ---------------------------------------------------------------------------
# Custom CSS — Premium Dark Theme
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* ── Import Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Global Overrides ── */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #111827 50%, #0f172a 100%);
    font-family: 'Inter', sans-serif;
    color: #e2e8f0;
}

/* Hide default Streamlit header/footer */
header[data-testid="stHeader"] { background: transparent !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* ── Hero Title ── */
.hero-title {
    text-align: center;
    padding: 1.5rem 0 0.3rem 0;
}
.hero-title h1 {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #60a5fa, #a78bfa, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.hero-title p {
    color: #94a3b8;
    font-size: 1.05rem;
    font-weight: 400;
}

/* ── Config Bar ── */
.config-bar {
    background: linear-gradient(135deg, #1e293b 0%, #1a2332 100%);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.config-bar-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #60a5fa;
    margin-bottom: 0.2rem;
}
.config-bar-sub {
    font-size: 0.82rem;
    color: #94a3b8;
    margin-bottom: 0.8rem;
}

/* ── Selectbox styling ── */
.stSelectbox > div > div {
    background: #0f172a !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
}

/* ── Metric override ── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1e293b, #1a2332);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    transition: transform 0.2s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-color: #60a5fa;
}
[data-testid="stMetricLabel"] { color: #94a3b8 !important; }
[data-testid="stMetricValue"] { color: #f1f5f9 !important; font-weight: 700 !important; }

/* ── Section Headers ── */
.section-header {
    margin: 2.5rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #334155;
}
.section-header h2 {
    font-size: 1.5rem;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 0.2rem;
}

</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# HERO TITLE
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-title">
    <h1>🔎 Screener Pro</h1>
    <p>Sort through vital market parameters and breakout signals instantly.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Data Initialization
# ---------------------------------------------------------------------------
def safe_millify(val, precision=2):
    try:
        v = float(val)
        if math.isnan(v) or math.isinf(v): return 'N/A'
        return millify(v, precision=precision)
    except Exception:
        return 'N/A'

def safe_round(val, decimals=2):
    try:
        v = float(val)
        if math.isnan(v) or math.isinf(v): return 'N/A'
        return round(v, decimals)
    except Exception:
        return 'N/A'

@st.cache_data
def load_symbols():
    try:
        csv = pd.read_csv('symbols.csv')
        return [s + ".NS" for s in csv['Symbol'].tolist()]
    except Exception:
        return ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"]

symbol_list = load_symbols()
try:
    default_idx = symbol_list.index("RELIANCE.NS")
except ValueError:
    default_idx = 0

# ═══════════════════════════════════════════════════════════════════════════
# CONFIG BAR
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="config-bar">
    <div class="config-bar-title">⚙️ Select Target</div>
    <div class="config-bar-sub">Choose a stock to analyze its core financial metrics and active signals</div>
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns([1, 2])
with c1:
    ticker_input = st.selectbox('Enter or Choose stock', symbol_list, index=default_idx, label_visibility='collapsed')

# ---------------------------------------------------------------------------
# Fetch Data
# ---------------------------------------------------------------------------
start_input = dt.datetime.today() - dt.timedelta(120)
end_input = dt.datetime.today()

with st.spinner(f"Analyzing metrics for {ticker_input}..."):
    df = yf.download(ticker_input, start_input, end_input, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date']).dt.date

if df.empty:
    st.error("❌ No data found for the selected ticker. Please try another stock.")
    st.stop()

stock = yf.Ticker(ticker_input)
info = stock.info

def to_scalar(val):
    if hasattr(val, 'values'): return val.values[0]
    return val

closing_price = to_scalar(round(df['Close'].iloc[-1:], 2))
sma_df = calc_moving_average(df, 12)
sma_val = to_scalar(sma_df['sma'].iloc[-1:])
ema_val = to_scalar(sma_df['ema'].iloc[-1:])

macd_df = calc_macd(df)
ema26_val = to_scalar(macd_df['ema26'].iloc[-1:])
macd_val = to_scalar(macd_df['macd'].iloc[-1:])
signal_val = to_scalar(macd_df['signal'].iloc[-1:])

rsi_df = RSI(df, 14)
rsi_val = round(to_scalar(rsi_df['RSI'].iloc[-1:]), 2)
adx_series = ADX(df, 14)
adx_val = round(to_scalar(adx_series.iloc[-1:]), 2)

breaking_out = is_breaking_out(df)
consolidating = is_consolidating(df)

def safe_info(key, default='N/A'):
    v = info.get(key)
    return v if v is not None else default

# ═══════════════════════════════════════════════════════════════════════════
# METRICS DISPLAY
# ═══════════════════════════════════════════════════════════════════════════

st.markdown('<div class="section-header"><h2>📊 Core Trading Signals</h2></div>', unsafe_allow_html=True)
s1, s2, s3, s4 = st.columns(4)
s1.metric('Recommendation', str(safe_info('recommendationKey', 'N/A')).upper())
s2.metric('Breaking Out?', "Yes 🚀" if breaking_out else "No")
s3.metric('Consolidating?', "Yes ⏳" if consolidating else "No")
s4.metric('Closing Price', f"₹{safe_millify(closing_price)}")

st.markdown('<div class="section-header"><h2>📈 Momentum & Technicals</h2></div>', unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)
m1.metric('RSI (14)', safe_round(rsi_val))
m2.metric('ADX (14)', safe_round(adx_val))
m3.metric('MACD Line', safe_round(macd_val, 4))
m4.metric('MACD Signal', safe_round(signal_val, 4))

m11, m22, m33, m44 = st.columns(4)
m11.metric('SMA (12)', safe_millify(sma_val))
m22.metric('EMA (12)', safe_millify(ema_val))
m33.metric('EMA (26)', safe_millify(ema26_val))
m44.metric('50 Day Avg', safe_millify(safe_info('fiftyDayAverage', 0)))

st.markdown('<div class="section-header"><h2>🏢 Financial Health & Margins</h2></div>', unsafe_allow_html=True)
f1, f2, f3, f4 = st.columns(4)
f1.metric('Current Ratio', safe_round(safe_info('currentRatio', 0), 2))
f2.metric('Return on Assets', safe_round(safe_info('returnOnAssets', 0), 4))
f3.metric('Debt to Equity', safe_round(safe_info('debtToEquity', 0), 2))
f4.metric('Return on Equity', safe_round(safe_info('returnOnEquity', 0), 4))

f11, f22, f33, f44 = st.columns(4)
f11.metric('EBITDA Margin', safe_round(safe_info('ebitdaMargins', 0), 4))
f22.metric('Profit Margin', safe_round(safe_info('profitMargins', 0), 4))
f33.metric('Gross Margin', safe_round(safe_info('grossMargins', 0), 4))
f44.metric('Operating Margin', safe_round(safe_info('operatingMargins', 0), 4))

st.markdown('<div class="section-header"><h2>📉 Price Extremes</h2></div>', unsafe_allow_html=True)
p1, p2, p3, p4 = st.columns(4)
p1.metric('52 Week Low', safe_millify(safe_info('fiftyTwoWeekLow', 0)))
p2.metric('52 Week High', safe_millify(safe_info('fiftyTwoWeekHigh', 0)))
p3.metric('Market Day Low', safe_millify(safe_info('regularMarketDayLow', 0)))
p4.metric('Market Day High', safe_millify(safe_info('regularMarketDayHigh', 0)))

