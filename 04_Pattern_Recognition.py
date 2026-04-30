import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
import plotly.graph_objects as go
from patterns import candlestick_patterns
import talib

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Pattern Recognition Pro", layout="wide")

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

/* ── Selectbox styling ── */
.stSelectbox > div > div, .stRadio > div {
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
}

/* ── Dataframe / Table ── */
.stDataFrame { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# HERO TITLE
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-title">
    <h1>🎯 Pattern Recognition Pro</h1>
    <p>Automated candlestick pattern scanning and trendline detection.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Data Initialization
# ---------------------------------------------------------------------------
@st.cache_data
def load_symbols():
    try:
        csv = pd.read_csv('symbols.csv')
        return [s + ".NS" for s in csv['Symbol'].tolist()]
    except Exception:
        return ["VISHWARAJ.NS", "RELIANCE.NS", "TCS.NS", "INFY.NS"]

symbol_list = load_symbols()
try:
    default_idx = symbol_list.index("VISHWARAJ.NS")
except ValueError:
    default_idx = 0

# ═══════════════════════════════════════════════════════════════════════════
# CONFIG BAR
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="config-bar">
    <div class="config-bar-title">⚙️ Select Target & Preferences</div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1.5, 1, 1])
with c1:
    ticker_input = st.selectbox('Stock Symbol', symbol_list, index=default_idx, label_visibility='collapsed')
with c2:
    show_chart = st.radio("Display Chart", ('Yes', 'No'), horizontal=True, label_visibility='collapsed')
with c3:
    chart_style = st.radio("Chart Type", ('Candlestick', 'Line Chart'), horizontal=True, label_visibility='collapsed')

# ---------------------------------------------------------------------------
# CHART DISPLAY
# ---------------------------------------------------------------------------
if show_chart == 'Yes':
    st.markdown('<div class="section-header"><h2>📈 Historical Chart</h2></div>', unsafe_allow_html=True)
    
    start_input = dt.datetime.today() - dt.timedelta(90)
    end_input = dt.datetime.today()

    with st.spinner("Loading chart data..."):
        hist_price = yf.download(ticker_input, start_input, end_input, auto_adjust=True)
        if isinstance(hist_price.columns, pd.MultiIndex):
            hist_price.columns = hist_price.columns.get_level_values(0)
        hist_price = hist_price.reset_index()
        hist_price['Date'] = pd.to_datetime(hist_price['Date']).dt.date

    fig = go.Figure()
    if chart_style == 'Line Chart':
        fig.add_trace(go.Scatter(x=hist_price['Date'], y=hist_price['Close'], name='Closing price', line=dict(color='#3b82f6', width=2)))
    else:
        fig.add_trace(go.Candlestick(
            x=hist_price['Date'],
            open=hist_price['Open'], high=hist_price['High'],
            low=hist_price['Low'], close=hist_price['Close'],
            name='OHLC',
            increasing_line_color='#34d399', decreasing_line_color='#f87171'
        ))
    
    fig.update_layout(
        height=500, template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,23,42,0.8)',
        hovermode='x unified', margin=dict(l=0, r=0, t=30, b=0),
        xaxis_rangeslider_visible=False
    )
    fig.update_yaxes(tickprefix='₹ ')
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
# PATTERN SCANNING
# ═══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header"><h2>🔍 Pattern Scanner Results</h2></div>', unsafe_allow_html=True)

with st.spinner("Scanning all candlestick patterns via TA-Lib..."):
    start_scan = dt.datetime.today() - dt.timedelta(365)
    end_scan = dt.datetime.today()
    df = yf.download(ticker_input, start_scan, end_scan, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date']).dt.date

if df.empty:
    st.error("❌ No data available for pattern scanning.")
    st.stop()

for candle, name in candlestick_patterns.items():
    try:
        df[candle] = getattr(talib, candle)(
            df['Open'].astype(float),
            df['High'].astype(float),
            df['Low'].astype(float),
            df['Close'].astype(float)
        )
    except Exception:
        df[candle] = 0

pattern_cols = list(candlestick_patterns.keys())
tmp_df = df[pattern_cols].copy()
tmp_df_T = tmp_df.T
tmp_last = tmp_df_T.iloc[:, -1].tolist()

signal_df = pd.DataFrame()
signal_df['Pattern Name'] = list(candlestick_patterns.values())
signal_df['Signal'] = tmp_last
signal_df['Signal'] = signal_df['Signal'].map({0: 'Neutral', -100: 'Bearish', 100: 'Bullish'})
signal_df['Signal'] = signal_df['Signal'].fillna('Neutral')

bullish_count = len(signal_df[signal_df['Signal'] == 'Bullish'])
bearish_count = len(signal_df[signal_df['Signal'] == 'Bearish'])
neutral_count = len(signal_df[signal_df['Signal'] == 'Neutral'])

col_bull, col_bear, col_neu = st.columns(3)
col_bull.metric('🟢 Bullish Signals', bullish_count)
col_bear.metric('🔴 Bearish Signals', bearish_count)
col_neu.metric('⚪ Neutral Patterns', neutral_count)

st.markdown("<br>", unsafe_allow_html=True)

def color_signal(val):
    if val == 'Bullish': return 'background-color: rgba(52, 211, 153, 0.2); color: #34d399; font-weight: bold;'
    elif val == 'Bearish': return 'background-color: rgba(248, 113, 113, 0.2); color: #f87171; font-weight: bold;'
    return 'color: #94a3b8;'

# Style dataframe for dark theme
styled_df = signal_df.style.map(color_signal, subset=['Signal']) \
    .set_properties(**{
        'background-color': '#1e293b',
        'color': '#f1f5f9',
        'border-color': '#334155'
    })

st.dataframe(styled_df, use_container_width=True, height=600)
