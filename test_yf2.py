import pandas as pd
import yfinance as yf
import datetime as dt

start = dt.datetime.today() - dt.timedelta(5 * 365)
end = dt.datetime.today()

raw = yf.download("TRIDENT.NS", start, end, auto_adjust=True)
print("columns before:")
print(raw.columns)

if isinstance(raw.columns, pd.MultiIndex):
    raw.columns = raw.columns.get_level_values(0)
    
raw = raw.reset_index()
print("columns after reset_index:")
print(raw.columns)

try:
    raw['Date'] = pd.to_datetime(raw['Date']).dt.date
    print("success")
except Exception as e:
    import traceback
    traceback.print_exc()
