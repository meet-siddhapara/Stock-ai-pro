import pandas as pd
import numpy as np
import tensorflow as tf
import random as rn
import yfinance as yf
import streamlit as st
import datetime as dt
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Fixed seeds for reproducibility
np.random.seed(1)
tf.random.set_seed(1)
rn.seed(1)

from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout
from keras.callbacks import EarlyStopping

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(page_title="StockAI Pro – Smart Forecasting & Coach", layout="wide")

# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------
if 'prediction_done' not in st.session_state:
    st.session_state.prediction_done = False
if 'results' not in st.session_state:
    st.session_state.results = {}
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'total_trades' not in st.session_state:
    st.session_state.total_trades = 0
if 'correct_trades' not in st.session_state:
    st.session_state.correct_trades = 0

# ---------------------------------------------------------------------------
# Premium Dark CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

.stApp {
    background: #0a0f18;
    font-family: 'Inter', sans-serif;
    color: #e2e8f0;
}
header[data-testid="stHeader"], #MainMenu, footer {
    display: none !important;
}

/* Hero */
.hero-title { text-align: center; padding: 2rem 0 1rem 0; }
.hero-title h1 {
    font-size: 2.8rem; font-weight: 800;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.hero-title p { color: #94a3b8; font-size: 1.1rem; font-weight: 500; }

/* Control Panel */
.control-panel {
    background: #111827; border: 1px solid #1f2937;
    border-radius: 16px; padding: 1.5rem;
    margin: 1rem 0 2rem 0; box-shadow: 0 10px 25px rgba(0,0,0,0.5);
}

/* Inputs */
.stSelectbox > div > div, .stNumberInput > div > div > input, .stSlider > div > div {
    background: #1f2937 !important; border: 1px solid #374151 !important;
    color: #e2e8f0 !important; border-radius: 8px !important;
}
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
    height: 44px !important; margin-top: 1.5rem !important; width: 100% !important;
}
.stButton > button:hover { box-shadow: 0 0 15px rgba(59,130,246,0.6) !important; }

/* Info Cards */
.info-card {
    background: rgba(31, 41, 55, 0.4); border: 1px solid #1f2937;
    border-radius: 14px; padding: 1.5rem; height: 100%;
}
.card-title { font-size: 1rem; font-weight: 700; color: #60a5fa; margin-bottom: 0.8rem; text-transform: uppercase; letter-spacing: 1px; }

/* Value Classes */
.val-green { color: #34d399; font-weight: 700; }
.val-red { color: #f87171; font-weight: 700; }
.val-normal { color: #94a3b8; }

.metric-box {
    background: rgba(31, 41, 55, 0.6); border: 1px solid #374151;
    border-radius: 12px; padding: 1rem; text-align: center; margin-bottom: 1rem;
}
.metric-box h3 { font-size: 1.6rem; color: #34d399; margin: 0; }
.metric-box p { color: #94a3b8; margin: 0; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; }

.score-badge {
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    color: white; border-radius: 30px; padding: 0.5rem 1.2rem;
    font-weight: 700; display: inline-block;
}

hr { border-color: #1f2937; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-title">
    <h1>StockAI Pro – Next-Day Forecast & Strategy</h1>
    <p>High-accuracy LSTM + Smart Investment Coach + Mistake Detection</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Functions for Indicators & Strategy
# ---------------------------------------------------------------------------
def add_technicals(df):
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    # Simple RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

# ---------------------------------------------------------------------------
# Symbols
# ---------------------------------------------------------------------------
try:
    csv_data = pd.read_csv('symbols.csv')
    symbol_list = [s + ".NS" for s in csv_data['Symbol'].tolist()]
except Exception:
    symbol_list = ["TRIDENT.NS", "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFC.NS"]

PERIOD_MAP = {
    '1 Month':  dt.timedelta(days=30),
    '3 Months': dt.timedelta(days=90),
    '6 Months': dt.timedelta(days=180),
    '1 Year':   dt.timedelta(days=365),
    '2 Years':  dt.timedelta(days=2*365),
    '5 Years':  dt.timedelta(days=5*365),
    '10 Years': dt.timedelta(days=10*365),
}

RISK_MAP = {
    'Low': 0.02,    # 2% stop loss
    'Medium': 0.05, # 5% stop loss
    'High': 0.10    # 10% stop loss
}

# ═══════════════════════════════════════════════════════════════════════════
# CONTROL PANEL (At Top)
# ═══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="control-panel">', unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns([1.5, 1.2, 1, 1.2, 1])

with col1:
    ticker = st.selectbox('🔍 Stock Symbol', symbol_list, index=0)
with col2:
    training_option = st.selectbox('📅 Range', list(PERIOD_MAP.keys()) + ['Custom'], index=4)
with col3:
    forecast_days = st.slider('⏳ Forecast', 1, 30, 7)
with col4:
    investment_amount = st.number_input('💰 Invest (₹)', value=10000, step=1000)
with col5:
    train_btn = st.button('🚀 Train AI')

if training_option == 'Custom':
    c1, c2, _ = st.columns([2, 2, 6])
    with c1: start_date = st.date_input('Start', dt.datetime.today() - dt.timedelta(days=365))
    with c2: end_date = st.date_input('End', dt.datetime.today())
else:
    end_date = dt.datetime.today().date()
    start_date = (dt.datetime.today() - PERIOD_MAP[training_option]).date()

st.markdown('</div>', unsafe_allow_html=True)

# Independant configuration for Model
LOOKBACK = 60
EPOCHS = 50

# ═══════════════════════════════════════════════════════════════════════════
# TRAINING & LOGIC
# ═══════════════════════════════════════════════════════════════════════════
if train_btn:
    with st.spinner('Fetching data & building AI...'):
        # 1. Fetch
        raw = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        
        if raw.empty or len(raw) < LOOKBACK + 10:
            st.error("❌ Not enough data points. Increase your training data range.")
            st.stop()

        raw = raw.reset_index()
        raw['Date'] = pd.to_datetime(raw['Date']).dt.date
        data = raw.sort_index(ascending=True)
        dataset = data['Close'].values.reshape(-1, 1)

        # 2. Scale
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(dataset)
        
        # 3. Train/Val Split (80/20)
        split = int(len(dataset) * 0.8)
        
        x_train, y_train = [], []
        for i in range(LOOKBACK, split):
            x_train.append(scaled_data[i-LOOKBACK:i, 0])
            y_train.append(scaled_data[i, 0])
        x_train, y_train = np.array(x_train), np.array(y_train)
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

        # 4. Model (3 Layer LSTM)
        model = Sequential([
            LSTM(100, return_sequences=True, input_shape=(LOOKBACK, 1)),
            Dropout(0.2),
            LSTM(100, return_sequences=True),
            Dropout(0.2),
            LSTM(50),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        
        early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
        history = model.fit(x_train, y_train, validation_split=0.1, batch_size=32, epochs=EPOCHS, verbose=0, callbacks=[early_stop])
        history_dict = history.history

        # 5. Test Set Evaluation
        x_test, y_test_actual = [], []
        for i in range(split, len(scaled_data)):
            x_test.append(scaled_data[i-LOOKBACK:i, 0])
            y_test_actual.append(dataset[i, 0])
        x_test = np.array(x_test)
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
        
        test_preds_scaled = model.predict(x_test, verbose=0)
        test_predictions = scaler.inverse_transform(test_preds_scaled)
        
        y_test_actual = np.array(y_test_actual).reshape(-1,1)
        test_dates = data['Date'].iloc[split:].tolist()

        mae = mean_absolute_error(y_test_actual, test_predictions)
        rmse = np.sqrt(mean_squared_error(y_test_actual, test_predictions))
        r2 = r2_score(y_test_actual, test_predictions)

        # 6. Future Prediction
        last_window = scaled_data[-LOOKBACK:].tolist()
        future_preds_scaled = []
        for _ in range(forecast_days):
            x_in = np.array(last_window[-LOOKBACK:]).reshape(1, LOOKBACK, 1)
            p = model.predict(x_in, verbose=0)[0,0]
            future_preds_scaled.append(p)
            last_window.append([p])
            
        future_preds = scaler.inverse_transform(np.array(future_preds_scaled).reshape(-1, 1)).flatten()
        last_date = data['Date'].iloc[-1]
        future_dates = [last_date + dt.timedelta(days=i) for i in range(1, forecast_days+1)]

        # 7. Calculations & Strategy logic
        current_price = float(data['Close'].iloc[-1])
        final_pred = float(future_preds[-1])
        change_pct = ((final_pred - current_price) / current_price) * 100
        
        tech = add_technicals(data)
        last_rsi = tech['RSI'].dropna().iloc[-1] if not tech['RSI'].dropna().empty else 50
        last_sma20 = tech['SMA_20'].dropna().iloc[-1] if not tech['SMA_20'].dropna().empty else current_price
        vol_trend = data['Volume'].tail(5).mean() > data['Volume'].tail(20).mean()
        
        # Strategy recommendation
        if change_pct > 2 and last_rsi < 70:
            rec = "BUY"
            rec_color = "val-green"
            risk_level = "Medium"
            reason = "Positive momentum detected with price target above current levels."
        elif change_pct < -2 or last_rsi > 70:
            rec = "SELL"
            rec_color = "val-red"
            risk_level = "High"
            reason = "Bearish outlook or Overbought conditions detected."
        else:
            rec = "HOLD"
            rec_color = "val-normal"
            risk_level = "Low"
            reason = "Price consolidation expected; no strong directional bias."

        # Explainable Reasons
        insights = []
        if change_pct > 0: insights.append("✔ Upward trend predicted by LSTM")
        else: insights.append("✖ Downward trend predicted by LSTM")
        if vol_trend: insights.append("✔ Increasing volume supports momentum")
        else: insights.append("✖ Low volume indicates weak trend")
        if current_price > last_sma20: insights.append("✔ Price trading above 20-day average")
        else: insights.append("✖ Price below short-term moving average")

        # Save to state
        st.session_state.results = {
            'data': data,
            'historical_dates': data['Date'].tolist(),
            'historical_close': data['Close'].tolist(),
            'test_dates': test_dates,
            'test_actual': y_test_actual.flatten(),
            'test_pred': test_predictions.flatten(),
            'future_dates': future_dates,
            'future_preds': future_preds,
            'mae': mae, 'rmse': rmse, 'r2': r2,
            'current_price': current_price,
            'final_pred': final_pred,
            'change_pct': change_pct,
            'rec': rec, 'rec_color': rec_color,
            'risk_level': risk_level, 'reason': reason,
            'inv': investment_amount,
            'insights': insights,
            'history': history_dict
        }
        st.session_state.prediction_done = True

# ═══════════════════════════════════════════════════════════════════════════
# DISPLAY SECTIONS
# ═══════════════════════════════════════════════════════════════════════════
if st.session_state.prediction_done:
    r = st.session_state.results
    
    # -------------------
    # 1️⃣ Single Plotly Chart
    # -------------------
    st.markdown("### 📈 Actual vs Predicted vs Forecast")
    fig = go.Figure()
    
    # Actual Historical (Faded)
    fig.add_trace(go.Scatter(x=r['historical_dates'], y=r['historical_close'], name='Actual (Hist)', line=dict(color='#3b82f6', width=2), opacity=0.3))
    # Test Actual vs Predicted
    fig.add_trace(go.Scatter(x=r['test_dates'], y=r['test_actual'], name='Actual (Test)', line=dict(color='#3b82f6', width=2)))
    fig.add_trace(go.Scatter(x=r['test_dates'], y=r['test_pred'], name='Predicted (Test)', line=dict(color='#f97316', width=2)))
    # Future Forecast (Green Dashed)
    fig.add_trace(go.Scatter(x=r['future_dates'], y=r['future_preds'], name='Forecast', line=dict(color='#22c55e', width=3, dash='dash')))
    
    fig.update_layout(height=500, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(13,17,28,0.8)',
                      xaxis_title='Date', yaxis_title='Price (₹)', legend=dict(orientation='h', yanchor='bottom', y=-0.2), margin=dict(l=50, r=20, t=20, b=80))
    st.plotly_chart(fig, use_container_width=True)

    # -------------------
    # 2️⃣ Metrics & Investment Analysis
    # -------------------
    c1, c2 = st.columns([1.2, 1])
    
    with c1:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">💰 Investment Calculator</div>', unsafe_allow_html=True)
        shares = int(r['inv'] // r['current_price'])
        future_val = shares * r['final_pred']
        profit = future_val - (shares * r['current_price'])
        p_color = "val-green" if profit >= 0 else "val-red"
        
        st.write(f"**Investment:** ₹{r['inv']:,}")
        st.write(f"**Buy Price:** ₹{r['current_price']:,.2f}")
        st.write(f"**Predicted Price ({forecast_days}d):** ₹{r['final_pred']:,.2f}")
        st.write(f"**Shares Purchased:** {shares}")
        st.markdown(f"**Expected P/L:** <span class='{p_color}'>₹{profit:,.2f} ({r['change_pct']:+.2f}%)</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">💡 Strategy Recommendation</div>', unsafe_allow_html=True)
        st.markdown(f"**Action:** <span class='{r['rec_color']}'>{r['rec']}</span>", unsafe_allow_html=True)
        st.write(f"**Entry Price:** ₹{r['current_price']:,.2f}")
        st.write(f"**Target Price:** ₹{r['final_pred']:,.2f}")
        sl = r['current_price'] * (1 - RISK_MAP[r['risk_level']]) if r['rec'] != "SELL" else r['current_price'] * (1 + RISK_MAP[r['risk_level']])
        st.write(f"**Stop Loss:** ₹{sl:,.2f}")
        st.write(f"**Risk Level:** {r['risk_level']}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # -------------------
    # 3️⃣ AI Coach & Insights
    # -------------------
    c3, c4 = st.columns([1, 1.2])
    
    with c3:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">❌ Mistake Detection (AI Coach)</div>', unsafe_allow_html=True)
        st.write("Test your skills: What would you do?")
        user_action = st.radio("Your Action", ["Buy", "Sell", "Hold"], horizontal=True)
        evaluate = st.button("⚖️ Evaluate Decision")
        
        if evaluate:
            st.session_state.total_trades += 1
            mistake = "No mistake detected."
            tip = "Good understanding of the current trend."
            
            if user_action == "Buy" and r['rec'] == "SELL":
                mistake = "Bad Entry: Counter-trend buying"
                tip = "Avoid buying when the AI detects a strong downward trend or overbought conditions."
            elif user_action == "Sell" and r['rec'] == "BUY":
                mistake = "Bad Exit: Early selling"
                tip = "Uptrend is still strong. Consider holding longer or using a trailing stop-loss."
            elif user_action == "Hold" and r['rec'] != "HOLD":
                mistake = "Missed Opportunity"
                tip = "The AI detected a clear directional move. Indecision can cost profit."
            else:
                st.session_state.correct_trades += 1
            
            st.markdown(f"**Feedback:** <span class='val-red' if 'mistake' in mistake.lower() else 'val-green'>{mistake}</span>", unsafe_allow_html=True)
            st.info(f"🎓 **Tip:** {tip}")
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🧠 AI Insights (Explainable Reasoning)</div>', unsafe_allow_html=True)
        st.write(f"**Reason for {r['rec']} Prediction:**")
        for insight in r['insights']:
            st.write(insight)
        st.write(f"*Insight: {r['reason']}*")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # Forecast Values
    st.markdown("**📢 Next N Days Forecast List:**")
    for i, val in enumerate(r['future_preds']):
        st.write(f"Day {i+1}: ₹{val:,.2f}")

    # Accuracy Score
    st.markdown(f"<div class='score-badge'>Coach Accuracy: {(st.session_state.correct_trades/st.session_state.total_trades*100) if st.session_state.total_trades > 0 else 0:.1f}%</div>", unsafe_allow_html=True)
