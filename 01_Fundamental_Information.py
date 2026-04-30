import streamlit as st
import yfinance as yf
import datetime as dt
import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Fundamental Analysis Pro", layout="wide")

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

/* ── Feature Cards ── */
.feature-card {
    background: linear-gradient(135deg, #1e293b, #1a2332);
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 1.3rem;
    min-height: 120px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 12px rgba(0,0,0,0.2);
    margin-bottom: 1rem;
}
.feature-card:hover {
    border-color: #60a5fa;
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(96,165,250,0.15);
}
.feature-card .icon {
    font-size: 1.8rem;
    margin-bottom: 0.4rem;
}
.feature-card h4 {
    font-size: 0.85rem;
    font-weight: 600;
    color: #94a3b8;
    margin-bottom: 0.2rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.feature-card p {
    font-size: 1.05rem;
    font-weight: 600;
    color: #f1f5f9;
    line-height: 1.4;
    margin: 0;
}

/* ── Section Headers ── */
.section-header {
    margin: 2.5rem 0 1rem 0;
}
.section-header h2 {
    font-size: 1.5rem;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 0.2rem;
}
.section-header p {
    color: #94a3b8;
    font-size: 0.95rem;
}

/* ── Selectbox / Input styling ── */
.stSelectbox > div > div,
.stDateInput > div > div > input,
.stRadio > div {
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

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #1e293b !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* ── Dataframe ── */
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* ── Download Button ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #10b981, #059669) !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 15px rgba(16,185,129,0.4) !important;
}

</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# HERO TITLE
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-title">
    <h1>🏢 Fundamental Analysis Pro</h1>
    <p>Deep insights, historical data, and financial health at a glance.</p>
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
    <div class="config-bar-title">⚙️ Configure Analysis</div>
    <div class="config-bar-sub">Select a stock and timeframe for historical charts</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1])

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

with col4:
    st.caption('**Chart Style**')
    chart_style = st.radio("Style", ('Candlestick', 'Line Chart'), horizontal=True, label_visibility='collapsed')

# ---------------------------------------------------------------------------
# Fetch Company Info
# ---------------------------------------------------------------------------
with st.spinner(f"Loading data for {ticker}..."):
    stock = yf.Ticker(ticker)
    info = stock.info

long_name = info.get('longName') or info.get('shortName') or ticker
sector = info.get('sector') or 'N/A'
industry = info.get('industry') or 'N/A'
phone = info.get('phone') or 'N/A'
address1 = info.get('address1') or ''
city = info.get('city') or ''
zip_code = info.get('zip') or ''
country = info.get('country') or ''
address_str = ', '.join(filter(None, [address1, city, zip_code, country])) or 'N/A'
website = info.get('website') or 'N/A'
business_summary = info.get('longBusinessSummary') or 'No summary available.'

# ═══════════════════════════════════════════════════════════════════════════
# COMPANY DETAILS
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="section-header">
    <h2>{long_name}</h2>
    <p>Company Overview & Metrics</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="feature-card">
        <div class="icon">🏭</div>
        <h4>Sector</h4>
        <p>{sector}</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="feature-card">
        <div class="icon">⚙️</div>
        <h4>Industry</h4>
        <p>{industry}</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="feature-card">
        <div class="icon">📍</div>
        <h4>Location</h4>
        <p style="font-size: 0.9rem;">{address_str}</p>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="feature-card">
        <div class="icon">🌐</div>
        <h4>Website & Phone</h4>
        <p style="font-size: 0.9rem;">{website}<br>{phone}</p>
    </div>
    """, unsafe_allow_html=True)

with st.expander('📖 See detailed business summary'):
    st.write(business_summary)

st.markdown('<br>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# HISTORICAL CHARTS
# ═══════════════════════════════════════════════════════════════════════════
hist_price = yf.download(ticker, start_input, end_input, auto_adjust=True)

if isinstance(hist_price.columns, pd.MultiIndex):
    hist_price.columns = hist_price.columns.get_level_values(0)
hist_price = hist_price.reset_index()

if not hist_price.empty:
    hist_price['Date'] = pd.to_datetime(hist_price['Date']).dt.date

    @st.cache_data
    def convert_df(df):
        return df.to_csv().encode('utf-8')

    historical_csv = convert_df(hist_price)
    
    st.markdown(f"""
    <div class="section-header">
        <h2>📈 Historical Performance</h2>
        <p>Price action from {start_input} to {end_input}</p>
    </div>
    """, unsafe_allow_html=True)

    fig = go.Figure()

    if chart_style == 'Line Chart':
        fig.add_trace(go.Scatter(
            x=hist_price['Date'], y=hist_price['Close'],
            name='Closing price', line=dict(color='#3b82f6', width=2),
            fill='tozeroy', fillcolor='rgba(59,130,246,0.1)'
        ))
    else:
        fig.add_trace(go.Candlestick(
            x=hist_price['Date'],
            open=hist_price['Open'], high=hist_price['High'],
            low=hist_price['Low'], close=hist_price['Close'],
            name='OHLC',
            increasing_line_color='#34d399', decreasing_line_color='#f87171'
        ))

    fig.update_layout(
        height=550, template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,23,42,0.8)',
        hovermode='x unified', margin=dict(l=0, r=0, t=30, b=0),
        xaxis_rangeslider_visible=False
    )
    fig.update_yaxes(tickprefix='₹ ')
    st.plotly_chart(fig, use_container_width=True)

    st.download_button(
        label="📥 Download historical data (CSV)",
        data=historical_csv,
        file_name=f'{ticker}_historical_data.csv',
        mime='text/csv',
    )
else:
    st.warning("⚠️ No historical data found for the selected date range.")

st.markdown('<hr>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# FINANCIAL STATEMENTS
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
    <h2>📑 Financial Statements</h2>
    <p>Deep dive into the company's financial health</p>
</div>
""", unsafe_allow_html=True)

def safe_financial_table(df_raw, label):
    if df_raw is None or df_raw.empty:
        st.info(f"No {label} data available for this stock.")
        return
    try:
        df_raw = df_raw.copy()
        df_raw.columns = df_raw.columns.date
        numeric_df = df_raw.apply(pd.to_numeric, errors='coerce').dropna(how='all')
        
        if numeric_df.empty:
            st.info(f"No numeric {label} data available.")
            return
            
        numeric_df = numeric_df.replace([float('inf'), float('-inf')], pd.NA).fillna(0).astype('int64')
        
        # Style dataframe for dark theme
        styled_df = numeric_df.style.format("{:,}") \
            .set_properties(**{
                'background-color': '#1e293b',
                'color': '#f1f5f9',
                'border-color': '#334155'
            }) \
            .highlight_max(axis=1, color='#059669') \
            .highlight_min(axis=1, color='#991b1b')

        st.dataframe(styled_df, height=350, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not display {label}: {e}")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    '📅 Quarterly Results', '💰 Profit & Loss', '⚖️ Balance Sheet', '💵 Cash Flows', '🎁 Splits & Dividends'
])

with tab1:
    st.markdown("**(QoQ) Summary of unaudited financial statements for the last few quarters.**")
    quarterly_results = stock.quarterly_income_stmt
    safe_financial_table(quarterly_results, 'Quarterly Results')

with tab2:
    st.markdown("**Annual summary of revenue, expenses, and profit.**")
    financials = stock.income_stmt
    safe_financial_table(financials, 'Profit & Loss')

with tab3:
    st.markdown("**Reports the company's assets, liabilities, and shareholder equity.**")
    balance = stock.balance_sheet
    safe_financial_table(balance, 'Balance Sheet')

with tab4:
    st.markdown("**Net amount of cash being transferred in and out of the company.**")
    cf = stock.cash_flow
    safe_financial_table(cf, 'Cash Flows')

with tab5:
    st.markdown("**Historical splits and dividend payouts.**")
    try:
        actions = stock.actions
        if actions is not None and not actions.empty:
            actions.index = actions.index.date
            
            styled_actions = actions.style.format("{:,.2f}") \
                .set_properties(**{
                    'background-color': '#1e293b',
                    'color': '#f1f5f9',
                    'border-color': '#334155'
                })
                
            st.dataframe(styled_actions, use_container_width=True)
        else:
            st.info("No splits or dividends data available.")
    except Exception as e:
        st.warning(f"Could not load splits/dividends: {e}")
