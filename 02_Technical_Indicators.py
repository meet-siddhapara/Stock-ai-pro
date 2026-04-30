from finta import TA
import ta
import yfinance as yf
import streamlit as st
import datetime as dt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from functions import calc_moving_average, calc_macd, calc_bollinger, ATR, RSI, ADX, OBV

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Technical Indicators Pro", layout="wide")

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

/* ── Section Headers ── */
.section-header {
    margin: 2.5rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #334155;
}
.section-header h2 {
    font-size: 1.8rem;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 0.2rem;
}
.section-header p {
    color: #94a3b8;
    font-size: 0.95rem;
}

/* ── Info Blocks ── */
.info-block {
    background: rgba(30, 41, 59, 0.5);
    border-left: 4px solid #60a5fa;
    padding: 1rem 1.2rem;
    border-radius: 0 8px 8px 0;
    margin-bottom: 1.5rem;
    font-size: 0.95rem;
    color: #cbd5e1;
}

/* ── Selectbox / Input styling ── */
.stSelectbox > div > div,
.stDateInput > div > div > input {
    background: #0f172a !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
}

/* ── Button styling ── */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(59,130,246,0.5) !important;
}

</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# HERO TITLE
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-title">
    <h1>📈 Technical Indicators Pro</h1>
    <p>Advanced charting & momentum tools to decode market trends.</p>
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
    <div class="config-bar-title">⚙️ Configure Indicators</div>
    <div class="config-bar-sub">Select a stock and timeframe to generate technical charts</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1.5, 1, 1])

min_value = dt.datetime.today() - dt.timedelta(days=10 * 365)
max_value = dt.datetime.today()

with col1:
    st.caption('**Select Stock**')
    ticker = st.selectbox('Stock', symbol_list, index=default_idx, label_visibility='collapsed')

with col2:
    st.caption('**Start Date**')
    start_input = st.date_input('Start Date', value=max_value - dt.timedelta(days=180), min_value=min_value, max_value=max_value, label_visibility='collapsed')

with col3:
    st.caption('**End Date**')
    end_input = st.date_input('End Date', value=max_value, min_value=min_value, max_value=max_value, label_visibility='collapsed')

# ---------------------------------------------------------------------------
# Fetch Data
# ---------------------------------------------------------------------------
with st.spinner(f"Loading data for {ticker}..."):
    df = yf.download(ticker, start_input, end_input, auto_adjust=True)

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)
df = df.reset_index()

if df.empty:
    st.error("❌ No data found for the selected ticker and date range. Please try a different stock or date range.")
    st.stop()

df['Date'] = pd.to_datetime(df['Date']).dt.date

# Custom Plotly Layout template function to keep things DRY
def apply_dark_layout(fig, title, height=500):
    fig.update_layout(
        height=height,
        title_text=title,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(15,23,42,0.8)',
        hovermode='x unified', 
        margin=dict(l=0, r=0, t=50, b=0),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
        xaxis_rangeslider_visible=False
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# OVERLAY INDICATORS
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
    <h2>📊 Overlay Indicators</h2>
    <p>Technical indicators that are plotted directly over the top of the price chart.</p>
</div>
""", unsafe_allow_html=True)

tab_ov1, tab_ov2, tab_ov3, tab_ov4 = st.tabs([
    "Moving Averages", "Hull Moving Average", "Bollinger Bands", "KAMA"
])

with tab_ov1:
    st.markdown("""
    <div class="info-block">
        <strong>Moving Averages (SMA & EMA)</strong>: Shows the average value of a stock's price over a period. Used to smooth out price data to form a trend following indicator.
    </div>
    """, unsafe_allow_html=True)
    df_ma = calc_moving_average(df, 14).reset_index(drop=True)
    figMA = go.Figure()
    figMA.add_trace(go.Scatter(x=df_ma['Date'], y=df_ma['Close'], name="Prices", line=dict(color='#94a3b8', width=2)))
    figMA.add_trace(go.Scatter(x=df_ma['Date'], y=df_ma['sma'], name='SMA (14)', line=dict(color='#3b82f6', width=2)))
    figMA.add_trace(go.Scatter(x=df_ma['Date'], y=df_ma['ema'], name='EMA (14)', line=dict(color='#f472b6', width=2)))
    figMA = apply_dark_layout(figMA, "Moving Averages (SMA & EMA)")
    st.plotly_chart(figMA, use_container_width=True)

with tab_ov2:
    st.markdown("""
    <div class="info-block">
        <strong>Hull Moving Average (HMA)</strong>: A directional trend indicator that is extremely fast and smooth, minimizing lag compared to traditional moving averages.
    </div>
    """, unsafe_allow_html=True)
    try:
        df_finta = df.copy()
        df_finta.columns = [c.lower() for c in df_finta.columns]
        hma_series = TA.HMA(df_finta, 14)
        fig_hma = go.Figure()
        fig_hma.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name='Close', line=dict(color='#94a3b8', width=2)))
        fig_hma.add_trace(go.Scatter(x=df['Date'], y=hma_series, name='HMA', line=dict(color='#a78bfa', width=2)))
        fig_hma = apply_dark_layout(fig_hma, "Hull Moving Average (HMA)")
        st.plotly_chart(fig_hma, use_container_width=True)
    except Exception as e:
        st.warning(f"HMA calculation failed: {e}")

with tab_ov3:
    st.markdown("""
    <div class="info-block">
        <strong>Bollinger Bands</strong>: Envelopes plotted at a standard deviation level above and below a simple moving average. Helpful in identifying volatility swings.
    </div>
    """, unsafe_allow_html=True)
    df_boll = calc_bollinger(df, 20).reset_index(drop=True)
    figBoll = go.Figure()
    figBoll.add_trace(go.Scatter(x=df_boll['Date'], y=df_boll['bolu'], name='Upper Band', line=dict(color='#fbbf24', width=1, dash='dot')))
    figBoll.add_trace(go.Scatter(x=df_boll['Date'], y=df_boll['bold'], name="Lower Band", line=dict(color='#fbbf24', width=1, dash='dot'), fill='tonexty', fillcolor='rgba(251,191,36,0.1)'))
    figBoll.add_trace(go.Scatter(x=df_boll['Date'], y=df_boll['sma'], name='SMA (20)', line=dict(color='#a78bfa', width=2)))
    figBoll.add_trace(go.Scatter(x=df_boll['Date'], y=df_boll['Close'], name="Close", line=dict(color='#34d399', width=2)))
    figBoll = apply_dark_layout(figBoll, "Bollinger Bands")
    st.plotly_chart(figBoll, use_container_width=True)

with tab_ov4:
    st.markdown("""
    <div class="info-block">
        <strong>Kaufman's Adaptive Moving Average (KAMA)</strong>: Designed to account for market noise or volatility. It closely follows prices when price swings are relatively small and noise is low.
    </div>
    """, unsafe_allow_html=True)
    try:
        kama = ta.momentum.KAMAIndicator(close=df['Close'], window=20, pow1=2, pow2=30)
        df['kama'] = kama.kama()
        fig_kama = go.Figure()
        fig_kama.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name="Close", line=dict(color='#94a3b8', width=2)))
        fig_kama.add_trace(go.Scatter(x=df['Date'], y=df['kama'], name="KAMA", line=dict(color='#ec4899', width=2)))
        fig_kama = apply_dark_layout(fig_kama, "KAMA Indicator")
        st.plotly_chart(fig_kama, use_container_width=True)
    except Exception as e:
        st.warning(f"KAMA calculation failed: {e}")

# ═══════════════════════════════════════════════════════════════════════════
# MOMENTUM INDICATORS
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
    <h2>🚀 Momentum Indicators</h2>
    <p>Shows the trend direction and measures the pace of the price fluctuation.</p>
</div>
""", unsafe_allow_html=True)

tab_mo1, tab_mo2, tab_mo3, tab_mo4, tab_mo5, tab_mo6 = st.tabs([
    "MACD", "RSI", "ADX", "Aroon", "TRIX", "STC"
])

with tab_mo1:
    st.markdown("""
    <div class="info-block">
        <strong>Moving Average Convergence Divergence (MACD)</strong>: A trend-following momentum indicator that shows the relationship between two moving averages.
    </div>
    """, unsafe_allow_html=True)
    df_macd = calc_macd(df).reset_index(drop=True)
    figMACD = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.6, 0.4], vertical_spacing=0.05)
    figMACD.add_trace(go.Scatter(x=df_macd['Date'], y=df_macd['Close'], name="Prices", line=dict(color='#94a3b8')), row=1, col=1)
    figMACD.add_trace(go.Scatter(x=df_macd['Date'], y=df_macd['macd'], name='MACD Line', line=dict(color='#3b82f6')), row=2, col=1)
    figMACD.add_trace(go.Scatter(x=df_macd['Date'], y=df_macd['signal'], name='Signal Line', line=dict(color='#f87171')), row=2, col=1)
    figMACD.add_bar(x=df_macd['Date'], y=df_macd['macd'] - df_macd['signal'], name='Histogram', marker_color='#a78bfa', row=2, col=1)
    figMACD = apply_dark_layout(figMACD, "MACD", height=600)
    st.plotly_chart(figMACD, use_container_width=True)

with tab_mo2:
    st.markdown("""
    <div class="info-block">
        <strong>Relative Strength Index (RSI)</strong>: Traditionally considered overbought when above 70 and oversold when below 30.
    </div>
    """, unsafe_allow_html=True)
    df_RSI = RSI(df, 14).reset_index(drop=True)
    fig_RSI = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.6, 0.4], vertical_spacing=0.05)
    fig_RSI.add_trace(go.Scatter(x=df_RSI['Date'], y=df_RSI['Close'], name='Close', line=dict(color='#94a3b8')), row=1, col=1)
    fig_RSI.add_trace(go.Scatter(x=df_RSI['Date'], y=df_RSI['RSI'], name='RSI', line=dict(color='#f59e0b')), row=2, col=1)
    fig_RSI.add_hline(y=70, line_dash='dash', line_color='#f87171', opacity=0.5, row=2, col=1)
    fig_RSI.add_hline(y=30, line_dash='dash', line_color='#34d399', opacity=0.5, row=2, col=1)
    fig_RSI = apply_dark_layout(fig_RSI, "RSI", height=600)
    st.plotly_chart(fig_RSI, use_container_width=True)

with tab_mo3:
    st.markdown("""
    <div class="info-block">
        <strong>Average Directional Index (ADX)</strong>: Measures the overall strength of a trend. A strong trend is present when ADX is > 25.
    </div>
    """, unsafe_allow_html=True)
    df['ADX'] = ADX(df, 14)
    fig_ADX = go.Figure()
    fig_ADX.add_trace(go.Scatter(x=df['Date'], y=df['ADX'], name='ADX', line=dict(color='#3b82f6', width=2)))
    fig_ADX.add_hline(y=25, line_dash='dash', line_color='#a78bfa', opacity=0.6)
    fig_ADX = apply_dark_layout(fig_ADX, "Average Directional Index (ADX)")
    st.plotly_chart(fig_ADX, use_container_width=True)

with tab_mo4:
    st.markdown("""
    <div class="info-block">
        <strong>Aroon Indicator</strong>: Identifies trend changes. Consists of 'Aroon up' (strength of uptrend) and 'Aroon down' (strength of downtrend).
    </div>
    """, unsafe_allow_html=True)
    try:
        aroon = ta.trend.AroonIndicator(high=df['High'], low=df['Low'], window=14)
        df['aroon_down'] = aroon.aroon_down()
        df['aroon_up'] = aroon.aroon_up()
        fig_aroon = go.Figure()
        fig_aroon.add_trace(go.Scatter(x=df['Date'], y=df['aroon_up'], name="Aroon Up", line=dict(color='#34d399', width=2)))
        fig_aroon.add_trace(go.Scatter(x=df['Date'], y=df['aroon_down'], name='Aroon Down', line=dict(color='#f87171', width=2)))
        fig_aroon = apply_dark_layout(fig_aroon, "Aroon Indicator")
        st.plotly_chart(fig_aroon, use_container_width=True)
    except Exception as e:
        st.warning(f"Aroon calculation failed: {e}")

with tab_mo5:
    st.markdown("""
    <div class="info-block">
        <strong>TRIX Indicator</strong>: Shows the percentage change in a moving average that has been smoothed exponentially three times.
    </div>
    """, unsafe_allow_html=True)
    try:
        trix = ta.trend.TRIXIndicator(close=df['Close'], window=14)
        df['trix'] = trix.trix()
        fig_trix = go.Figure()
        fig_trix.add_trace(go.Scatter(x=df['Date'], y=df['trix'], name='TRIX', line=dict(color='#60a5fa', width=2)))
        fig_trix.add_hline(y=0, line_dash='dash', line_color='#64748b', opacity=0.5)
        fig_trix = apply_dark_layout(fig_trix, "TRIX Indicator")
        st.plotly_chart(fig_trix, use_container_width=True)
    except Exception as e:
        st.warning(f"TRIX calculation failed: {e}")

with tab_mo6:
    st.markdown("""
    <div class="info-block">
        <strong>Schaff Trend Cycle (STC)</strong>: Suggests buying when it surges above the 25 level and selling when it drops below the 75 level.
    </div>
    """, unsafe_allow_html=True)
    try:
        df_finta2 = df.copy()
        df_finta2.columns = [c.lower() for c in df_finta2.columns]
        stc = TA.STC(df_finta2, 14)
        fig_stc = go.Figure()
        fig_stc.add_trace(go.Scatter(x=df['Date'], y=stc, name="STC", line=dict(color='#f472b6', width=2)))
        fig_stc.add_hline(y=75, line_dash='dash', line_color='#f87171', opacity=0.5)
        fig_stc.add_hline(y=25, line_dash='dash', line_color='#34d399', opacity=0.5)
        fig_stc = apply_dark_layout(fig_stc, "Schaff Trend Cycle (STC)")
        st.plotly_chart(fig_stc, use_container_width=True)
    except Exception as e:
        st.warning(f"STC calculation failed: {e}")

# ═══════════════════════════════════════════════════════════════════════════
# VOLUME & VOLATILITY
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
    <h2>📈 Volume & Volatility</h2>
    <p>Measure trading intensity and price range fluctuations.</p>
</div>
""", unsafe_allow_html=True)

tab_vv1, tab_vv2 = st.tabs(["On Balance Volume (OBV)", "Average True Range (ATR)"])

with tab_vv1:
    st.markdown("""
    <div class="info-block">
        <strong>On Balance Volume (OBV)</strong>: A technical trading momentum indicator that uses volume flow to predict changes in stock price.
    </div>
    """, unsafe_allow_html=True)
    df['obv'] = OBV(df)
    fig_OBV = go.Figure()
    fig_OBV.add_trace(go.Scatter(x=df['Date'], y=df['obv'], name='OBV', line=dict(color='#a78bfa', width=2), fill='tozeroy', fillcolor='rgba(167,139,250,0.1)'))
    fig_OBV = apply_dark_layout(fig_OBV, "On Balance Volume (OBV)")
    st.plotly_chart(fig_OBV, use_container_width=True)

with tab_vv2:
    st.markdown("""
    <div class="info-block">
        <strong>Average True Range (ATR)</strong>: Measures volatility by taking into account any gaps in the price movement.
    </div>
    """, unsafe_allow_html=True)
    df_ATR = ATR(df, 20)
    fig_ATR = go.Figure()
    fig_ATR.add_trace(go.Scatter(x=df_ATR['Date'], y=df_ATR['ATR'], name='ATR', line=dict(color='#fbbf24', width=2)))
    fig_ATR = apply_dark_layout(fig_ATR, "Average True Range (ATR)")
    st.plotly_chart(fig_ATR, use_container_width=True)
