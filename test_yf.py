import yfinance as yf
df = yf.download('RELIANCE.NS', period='1mo')
print(df.columns)
print(df.head())
