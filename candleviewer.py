import ccxt
import mplfinance as mpf
import pandas as pd
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import time

class CandleViewer:
    def __init__(self, exchange_name='binance', symbol='BTC/USDT', interval_sec=60, kline_limit=100, ma_periods=(25,)):
        self.symbol = symbol
        self.kline_limit = kline_limit
        self.interval_sec = interval_sec
        self.ma_periods = ma_periods  # Tuple of moving average periods

        # Initialize the exchange
        self.exchange = getattr(ccxt, exchange_name)()

        # Fetch initial candlestick data and convert to DataFrame
        self.data = self.fetch_initial_klines()

        # Initialize the last update time
        self.last_update_time = time.time()

        # Create the chart
        self.fig, self.ax = plt.subplots()

        # Start animation update
        self.ani = FuncAnimation(self.fig, self.update, interval=1000, cache_frame_data=False)
        plt.show()

    def fetch_initial_klines(self):
        """Fetch the initial candlestick data and convert to DataFrame format"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe=f"{self.interval_sec // 60}m", limit=self.kline_limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df

        except ccxt.NetworkError as e:
            print(f"Network error while fetching OHLCV data for {self.symbol}: {str(e)}")
            raise
        except ccxt.BadSymbol as e:
            print(f"Bad symbol error: The symbol '{self.symbol}' is not supported. Error: {str(e)}")
            raise
        except ccxt.ExchangeError as e:
            print(f"Invalid interval error: '{self.interval_sec}' might not be valid. Error: {str(e)}")
            raise
        except Exception as e:
            print(f"An unknown error occurred while fetching OHLCV data: {str(e)}")
            raise

    def fetch_latest_ticker(self):
        """Fetch the latest ticker data (current price)"""
        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            return {
                'price': ticker['last'],  # Latest price
                'volume': ticker['quoteVolume']  # Latest volume
            }

        except ccxt.NetworkError as e:
            print(f"Network error while fetching ticker data for {self.symbol}: {str(e)}")
            raise
        except ccxt.BadSymbol as e:
            print(f"Bad symbol error: The symbol '{self.symbol}' is not supported. Error: {str(e)}")
            raise
        except Exception as e:
            print(f"An unknown error occurred while fetching ticker data: {str(e)}")
            raise

    def update(self, frame):
        """Update the chart data"""
        now = time.time()
        try:
            ticker = self.fetch_latest_ticker()
        except Exception as e:
            print(f"Error during update: {e}")
            raise

        elapsed_time = now - self.last_update_time

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
            last_candle = self.data.iloc[-1]
            last_candle['high'] = max(last_candle['high'], latest_price)
            last_candle['low'] = min(last_candle['low'], latest_price)
            last_candle['close'] = latest_price
            self.data.iloc[-1] = last_candle

        if len(self.data) > self.kline_limit:
            self.data = self.data.iloc[1:]

        self.redraw_chart()

    def redraw_chart(self):
        """Redraw the candlestick chart with moving averages"""
        self.ax.clear()
        mpf.plot(
            self.data,
            type='candle',
            style='charles',
            ax=self.ax,
            show_nontrading=False,
            mav=self.ma_periods  # moving averages by mplfinance built-in function
        )
        self.ax.set_title(f'{self.symbol} Live Price')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Price (USDT)')


if __name__ == "__main__":
    candle_viewer = CandleViewer(symbol="BTC/USDT", interval_sec=60, ma_periods=(25,50,))
