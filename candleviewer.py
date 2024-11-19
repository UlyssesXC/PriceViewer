import ccxt
import mplfinance as mpf
import pandas as pd
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import time

class CandleViewer:
    def __init__(self, exchange_name='binance', symbol='BTC/USDT', interval_sec=60, kline_limit=100):
        self.symbol = symbol
        self.kline_limit = kline_limit
        self.interval_sec = interval_sec
        
        # Initialize the exchange
        self.exchange = getattr(ccxt, exchange_name)()
        
        # Fetch initial candlestick data and convert to DataFrame
        self.data = self.fetch_initial_klines()
        
        # Initialize the last update time
        self.last_update_time = time.time()
        
        # Create the chart
        self.fig, self.ax = plt.subplots()
        
        # Start animation update
        self.ani = FuncAnimation(self.fig, self.update, interval=1000, cache_frame_data=False)  # Refresh every 1 second
        plt.show()

    def fetch_initial_klines(self):
        # TODO: ERROR HANDLE
        """Fetch the initial candlestick data and convert to DataFrame format"""
        ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe=f"{self.interval_sec // 60}m", limit=self.kline_limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        """
        Data struct of ccxt (crypto currency price data):
        [
        [timestamp, open, high, low, close, volume],
        [timestamp, open, high, low, close, volume],
        ...
        ]
        """
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        # Print initial fetched data
        print("Initial K-line data fetched:\n", df)
        return df

    def fetch_latest_ticker(self):
        # TODO: ERROR HANDLE
        """Fetch the latest ticker data (current price)"""
        ticker = self.exchange.fetch_ticker(self.symbol)
        return {
            'price': ticker['last'],  # Latest price
            'volume': ticker['quoteVolume']  # Latest volume
        }

    def update(self, frame):
        """Update the chart data"""
        # print("Updating chart")
        now = time.time()
        ticker = self.fetch_latest_ticker()
        
        # Calculate elapsed time since the last full candle update
        elapsed_time = now - self.last_update_time

        # Get the latest price and volume
        latest_price = ticker['price']
        latest_volume = ticker['volume']

        if elapsed_time >= self.interval_sec:
            # Time to create a new candle
            new_candle = {
                'open': latest_price,
                'high': latest_price,
                'low': latest_price,
                'close': latest_price,
                'volume': latest_volume
            }
            self.data = pd.concat([self.data, pd.DataFrame([new_candle], index=[pd.Timestamp.now()])])
            self.last_update_time = now
        else:
            # Update the last candle dynamically
            last_candle = self.data.iloc[-1]
            last_candle['high'] = max(last_candle['high'], latest_price)
            last_candle['low'] = min(last_candle['low'], latest_price)
            last_candle['close'] = latest_price
            self.data.iloc[-1] = last_candle

        # Keep only the latest kline_limit rows
        if len(self.data) > self.kline_limit:
            self.data = self.data.iloc[1:]

        # Redraw the candlestick chart
        self.ax.clear()
        mpf.plot(self.data, type='candle', style='charles', ax=self.ax, show_nontrading=False)

        # Add title and labels
        self.ax.set_title(f'{self.symbol} Live Price')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Price (USDT)')

if __name__ == "__main__":
    candle_viewer = CandleViewer(symbol="BTC/USDT", interval_sec=60) # default paramter for class test
