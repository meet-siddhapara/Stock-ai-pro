import streamlit as st

st.set_page_config(page_title="StockAI Pro", layout="wide", page_icon="📈")

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

html, body, .stApp { background: #050c18 !important; font-family: 'Inter', sans-serif !important; color: #e2e8f0; }
footer, #MainMenu { display: none !important; }
.block-container { padding-top: 1rem !important; }

/* hero */
.hero { text-align: center; padding: 4rem 1rem 2.5rem; }
.badge {
    display: inline-block; background: rgba(59,130,246,0.15);
    border: 1px solid rgba(59,130,246,0.35); color: #60a5fa;
    border-radius: 50px; padding: 0.3rem 1.1rem;
    font-size: 0.75rem; font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; margin-bottom: 1.4rem;
}
.hero-title {
    font-size: 3.8rem; font-weight: 900; line-height: 1.1;
    background: linear-gradient(135deg, #e2e8f0 0%, #93c5fd 40%, #c084fc 75%, #f472b6 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin-bottom: 1rem;
}
.hero-sub { font-size: 1.15rem; color: #94a3b8; max-width: 560px; margin: 0 auto 2rem; line-height: 1.7; }

/* stat card */
.stat-card {
    background: #0f172a; border: 1px solid #1e293b;
    border-radius: 16px; padding: 1.6rem 1.2rem;
    text-align: center; height: 100%;
    transition: transform 0.25s, border-color 0.25s;
}
.stat-card:hover { transform: translateY(-4px); border-color: #4f46e5; }
.stat-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.stat-val {
    font-size: 1.7rem; font-weight: 800;
    background: linear-gradient(135deg, #60a5fa, #c084fc);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin-bottom: 0.3rem;
}
.stat-lbl { color: #475569; font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; }

/* feature card */
.feat-card {
    background: #0f172a; border: 1px solid #1e293b;
    border-radius: 16px; padding: 1.6rem 1.4rem; height: 100%;
    transition: transform 0.25s, border-color 0.25s, box-shadow 0.25s;
}
.feat-card:hover { transform: translateY(-5px); border-color: #4f46e5; box-shadow: 0 16px 40px rgba(0,0,0,0.5); }
.feat-icon {
    width: 48px; height: 48px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem; margin-bottom: 0.9rem;
}
.ic-blue   { background: rgba(59,130,246,0.15); border: 1px solid rgba(59,130,246,0.25); }
.ic-purple { background: rgba(139,92,246,0.15); border: 1px solid rgba(139,92,246,0.25); }
.ic-teal   { background: rgba(20,184,166,0.15);  border: 1px solid rgba(20,184,166,0.25); }
.ic-green  { background: rgba(16,185,129,0.15);  border: 1px solid rgba(16,185,129,0.25); }
.ic-amber  { background: rgba(245,158,11,0.15);  border: 1px solid rgba(245,158,11,0.25); }
.ic-pink   { background: rgba(236,72,153,0.15);  border: 1px solid rgba(236,72,153,0.25); }
.feat-title { font-size: 1rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.45rem; }
.feat-desc  { font-size: 0.85rem; color: #64748b; line-height: 1.6; }

/* why card */
.why-card {
    background: #0f172a; border: 1px solid #1e293b;
    border-radius: 14px; padding: 1.2rem 1.4rem;
    display: flex; gap: 1rem; align-items: flex-start;
    transition: border-color 0.25s, transform 0.25s;
}
.why-card:hover { border-color: #4f46e5; transform: translateX(4px); }
.why-dot {
    width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem; font-weight: 800; color: #fff;
}
.why-title { font-size: 0.95rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.2rem; }
.why-desc  { font-size: 0.82rem; color: #64748b; line-height: 1.5; }

/* cta */
.cta-box {
    background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(139,92,246,0.1));
    border: 1px solid rgba(99,102,241,0.25); border-radius: 24px;
    padding: 3.5rem 2rem; text-align: center; margin: 1rem 0;
}
.cta-title { font-size: 2.2rem; font-weight: 800; color: #f1f5f9; margin-bottom: 0.6rem; }
.cta-sub   { font-size: 1rem; color: #94a3b8; margin-bottom: 1.8rem; }

/* section label */
.sec-tag {
    display: inline-block; background: rgba(139,92,246,0.15);
    border: 1px solid rgba(139,92,246,0.3); color: #a78bfa;
    border-radius: 50px; padding: 0.28rem 0.9rem;
    font-size: 0.72rem; font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; margin-bottom: 0.7rem;
}
.sec-title { font-size: 2rem; font-weight: 800; color: #f1f5f9; margin-bottom: 0.4rem; }
.sec-sub   { font-size: 0.95rem; color: #475569; margin-bottom: 2rem; }

/* nav buttons override */
div[data-testid="stHorizontalBlock"] .stButton > button {
    background: #0f172a !important;
    border: 1px solid #1e293b !important;
    color: #94a3b8 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1rem !important;
    width: 100% !important;
    margin-top: 0 !important;
    transition: all 0.25s !important;
}
div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    border-color: #4f46e5 !important;
    color: #e2e8f0 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(0,0,0,0.4) !important;
}
/* main CTA button */
.cta-btn > div > button {
    background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-weight: 700 !important;
    font-size: 1.05rem !important; padding: 0.8rem 2.5rem !important;
    box-shadow: 0 4px 20px rgba(59,130,246,0.35) !important;
    width: auto !important; margin-top: 0 !important;
}
.divider { height: 1px; background: linear-gradient(90deg,transparent,rgba(99,102,241,0.25),transparent); margin: 2.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════
# HERO
# ═══════════════════════════════════
st.markdown("""
<div class="hero">
  <div class="badge">🚀 AI-Powered Stock Intelligence Platform</div>
  <div class="hero-title">StockAI Pro</div>
  <div class="hero-sub">Smart Forecasting, Strategy &amp; AI Trading Coach<br>for NSE-listed stocks — powered by Deep LSTM</div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns([3, 2, 3])
with c2:
    if st.button("🚀 Start Forecasting", key="hero_cta", use_container_width=True):
        st.switch_page("pages/05_Next-Day_Forecasting.py")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════
# STATS
# ═══════════════════════════════════
s1, s2, s3, s4 = st.columns(4)
stats = [
    ("📊", "1,700+", "NSE Stocks Covered"),
    ("📅", "10 Yrs", "Historical Data Range"),
    ("🤖", "LSTM", "Deep AI Model"),
    ("🎯", "30 Days", "Max Forecast Horizon"),
]
for col, (icon, val, lbl) in zip([s1, s2, s3, s4], stats):
    col.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon">{icon}</div>
        <div class="stat-val">{val}</div>
        <div class="stat-lbl">{lbl}</div>
    </div>""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════
# FEATURES
# ═══════════════════════════════════
st.markdown("""
<div style="text-align:center;">
  <div class="sec-tag">✦ Core Features</div>
  <div class="sec-title">Everything you need to trade smarter</div>
  <div class="sec-sub">Six powerful modules. One unified platform.</div>
</div>
""", unsafe_allow_html=True)

features = [
    ("ic-blue",   "📈", "Stock Forecasting",      "Deep LSTM neural network predicts future price movements with multi-day horizon and confidence signals."),
    ("ic-purple", "🧠", "AI Trading Coach",        "Simulate trades, get real-time feedback on mistakes, and learn from AI-powered coaching sessions."),
    ("ic-teal",   "📉", "Technical Indicators",    "11+ indicators — MACD, RSI, Bollinger Bands, ADX, KAMA and more — all interactive charts."),
    ("ic-green",  "🔍", "Stock Screener",          "Filter stocks by breakout signals, consolidation zones and key financial metrics automatically."),
    ("ic-amber",  "🎮", "Investment Simulator",    "Simulate ₹ ROI over any forecast period before risking real capital."),
    ("ic-pink",   "🕯",  "Pattern Recognition",    "Auto-scan candlestick patterns (Doji, Hammer, Engulfing) with bullish/bearish signals."),
]

row1 = st.columns(3)
row2 = st.columns(3)
for i, (col, (ic, emoji, title, desc)) in enumerate(zip(row1 + row2, features)):
    col.markdown(f"""
    <div class="feat-card">
        <div class="feat-icon {ic}">{emoji}</div>
        <div class="feat-title">{title}</div>
        <div class="feat-desc">{desc}</div>
    </div>""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════
# WHY STOCKAI PRO
# ═══════════════════════════════════
st.markdown("""
<div style="text-align:center;">
  <div class="sec-tag">✦ Why Choose Us</div>
  <div class="sec-title">Why StockAI Pro?</div>
  <div class="sec-sub">Built for serious learners and retail investors alike.</div>
</div>
""", unsafe_allow_html=True)

why_items = [
    ("AI-Based Price Prediction",     "Deep LSTM trained on real NSE historical data — not rule-based extrapolation."),
    ("Strategy Recommendation",       "BUY / SELL / HOLD signals with entry price, target, and stop-loss levels."),
    ("Mistake Detection Engine",       "AI coach flags counter-trend, early-sell, and bad-setup errors in simulated trades."),
    ("Adaptive Learning System",       "Score, accuracy % and skill-level tracking across all your trading simulations."),
    ("1700+ NSE Stocks",              "Full NSE coverage with up to 10 years of daily OHLCV data via Yahoo Finance."),
    ("No-Code, Instant Insights",     "Zero setup — select a stock, click Train, and get professional-grade forecasts."),
]

wc1, wc2 = st.columns(2)
for i, (title, desc) in enumerate(why_items):
    col = wc1 if i % 2 == 0 else wc2
    col.markdown(f"""
    <div class="why-card">
        <div class="why-dot">✓</div>
        <div>
            <div class="why-title">{title}</div>
            <div class="why-desc">{desc}</div>
        </div>
    </div><br>""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════
# QUICK NAV
# ═══════════════════════════════════
st.markdown("""
<div style="text-align:center;margin-bottom:1.2rem;">
  <div class="sec-tag">✦ Quick Access</div>
  <div class="sec-title">Jump to any module</div>
</div>
""", unsafe_allow_html=True)

n1, n2, n3, n4, n5 = st.columns(5)
with n1:
    if st.button("📊 Fundamental Info", use_container_width=True):
        st.switch_page("pages/01_Fundamental_Information.py")
with n2:
    if st.button("📉 Tech Indicators", use_container_width=True):
        st.switch_page("pages/02_Technical_Indicators.py")
with n3:
    if st.button("🔍 Screener", use_container_width=True):
        st.switch_page("pages/03_Screener.py")
with n4:
    if st.button("🕯 Patterns", use_container_width=True):
        st.switch_page("pages/04_Pattern_Recognition.py")
with n5:
    if st.button("🚀 Forecasting", use_container_width=True):
        st.switch_page("pages/05_Next-Day_Forecasting.py")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════
# CTA BOTTOM
# ═══════════════════════════════════
st.markdown("""
<div class="cta-box">
  <div class="cta-title">Start Your Smart Investing Journey</div>
  <div class="cta-sub">Select any NSE stock · Train the AI in seconds · Get multi-day forecasts with strategy insights</div>
</div>
""", unsafe_allow_html=True)

cc1, cc2, cc3 = st.columns([3, 2, 3])
with cc2:
    if st.button("🚀 Go to Forecasting →", key="cta_btn", use_container_width=True):
        st.switch_page("pages/05_Next-Day_Forecasting.py")

st.markdown("""
<div style="text-align:center;color:#1e293b;font-size:0.78rem;padding:2rem 0 1rem;">
  StockAI Pro &nbsp;·&nbsp; NSE Data via Yahoo Finance &nbsp;·&nbsp; Streamlit + TensorFlow
</div>
""", unsafe_allow_html=True)
