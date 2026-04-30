import pandas as pd
import numpy as np
import tensorflow as tf
import datetime as dt
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

ticker = "TRIDENT.NS"

def my_LSTM(ticker):
    try:
        start = dt.datetime.today() - dt.timedelta(5 * 365)
        end = dt.datetime.today()

        raw = yf.download(ticker, start, end, auto_adjust=True)

        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)

        if raw.empty:
            print("empty")
            return

        raw = raw.reset_index()
        raw['Date'] = pd.to_datetime(raw['Date']).dt.date

        data = raw.sort_index(ascending=True).copy()
        
        # print the close column to see if it's a series or dataframe
        print(type(data['Close']))
        print(data['Close'].head())

        new_data = pd.DataFrame({
            'Date': data['Date'].values,
            'Close': data['Close'].astype(float).values
        })
        new_data.index = new_data['Date']
        new_data.drop('Date', axis=1, inplace=True)

        dataset = new_data.values.astype(float)
        split = int(len(dataset) * 0.80)
        train_arr = dataset[0:split, :]
        valid_arr = dataset[split:, :]

        print(f"train length: {len(train_arr)}")
        
        if len(train_arr) < 60 or len(valid_arr) < 1:
            print("Not enough historical data")
            return

        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(dataset)

        x_train, y_train = [], []
        for i in range(60, len(train_arr)):
            x_train.append(scaled_data[i - 60:i, 0])
            y_train.append(scaled_data[i, 0])
        x_train, y_train = np.array(x_train), np.array(y_train)
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

        print("Building model...")
        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
        model.add(LSTM(units=50))
        model.add(Dense(1))
        model.compile(loss='mean_squared_error', optimizer='adam')
        model.fit(x_train, y_train, epochs=1, batch_size=1, verbose=0)
        
        print("Model fitted")
        
    except Exception as e:
        import traceback
        traceback.print_exc()

my_LSTM(ticker)
