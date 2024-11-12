import ccxt
import mplfinance as mpf
import pandas as pd
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt

class CandleViewer:
    def __init__(self, exchange_name='binance', symbol='BTC/USDT', interval_sec=60, kline_limit=100):
        self.symbol = symbol
        self.kline_limit = kline_limit
        
        # Convert interval from seconds to minutes for use in fetch_ohlcv and animation interval in milliseconds
        self.interval = f"{interval_sec // 60}m" if interval_sec >= 60 else f"{interval_sec}s"
        self.ani_interval = interval_sec * 1000  # milliseconds for FuncAnimation

        # Initialize the exchange
        self.exchange = getattr(ccxt, exchange_name)()
        
        # Fetch initial candlestick data and convert to DataFrame
        self.data = self.fetch_initial_klines()
        
        # Create the chart
        self.fig, self.ax = plt.subplots()
        
        # Start animation update
        self.ani = FuncAnimation(self.fig, self.update, interval=self.ani_interval, cache_frame_data=False)
        plt.show()

    def fetch_initial_klines(self):
        """Fetch the initial candlestick data and convert to DataFrame format"""
        ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe=self.interval, limit=self.kline_limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        # Print initial fetched data
        print("Initial K-line data fetched:\n", df)
        return df

    def fetch_latest_kline(self):
        """Fetch the latest candlestick data and convert to DataFrame format"""
        ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe=self.interval, limit=1)
        if ohlcv:
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Print the latest fetched data
            print("Latest K-line data fetched:\n", df)
            return df
        else:
            return None  # Return None if no data is fetched

    def calculate_rsi(self, data, period=14):
        """Calculate RSI based on the close prices with a given period"""
        delta = data['close'].diff(1)
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Print the latest RSI value
        latest_rsi = rsi.iloc[-1]
        print(f"RSI (period={period}): {latest_rsi:.2f}")
        
        return latest_rsi

    def update(self, frame):
        """Update the chart data"""
        print("Updating chart once")
        latest_df = self.fetch_latest_kline()
        
        if latest_df is not None:  # Check if valid data is fetched
            self.data = pd.concat([self.data, latest_df])
            if len(self.data) > self.kline_limit:
                self.data = self.data.iloc[1:]
            
            # Calculate and print RSI
            self.calculate_rsi(self.data)
            
            # Clear ax and redraw candlestick chart
            self.ax.clear()
            mpf.plot(self.data, type='candle', style='charles', ax=self.ax, show_nontrading=False)

            # Add title and labels
            self.ax.set_title(f'{self.symbol} Live Price')
            self.ax.set_xlabel('Time')
            self.ax.set_ylabel('Price (USDT)')

def get_top_10_pairs_by_volume(exchange_name='binance'):
    """Get the top 10 trading pairs by volume"""
    print("Fetching top 10 trading pairs by volume...")
    exchange = getattr(ccxt, exchange_name)()
    markets = exchange.fetch_tickers()
    
    # Extract symbol and volume information
    data = []
    for symbol, ticker in markets.items():
        if 'quoteVolume' in ticker:  # Ensure the field exists in the data
            data.append({
                'symbol': symbol,
                'volume': ticker['quoteVolume']  # Use quote volume for consistency
            })
    
    # Convert to DataFrame for easy sorting and display
    df = pd.DataFrame(data)
    
    # Sort by volume in descending order and select the top 10
    top_10 = df.sort_values(by='volume', ascending=False).head(10)
    
    # Print the top 10 pairs by volume
    print("Top 10 trading pairs by volume:")
    print(top_10)
    return top_10['symbol'].tolist()

# Command-line interface for user input
if __name__ == "__main__":
    top_10_pairs = get_top_10_pairs_by_volume()

    # Prompt user to select a trading pair from the top 10 or enter their own
    print("\nSelect a trading pair from the top 10 or enter your own:")
    for i, pair in enumerate(top_10_pairs, 1):
        print(f"{i}. {pair}")
    
    choice = input("Enter the number of the trading pair or type a symbol (e.g., BTC/USDT): ").strip()
    
    # Determine the selected symbol
    if choice.isdigit() and 1 <= int(choice) <= len(top_10_pairs):
        symbol = top_10_pairs[int(choice) - 1]
    else:
        symbol = choice
    
    # Get interval in seconds
    interval_sec = int(input("Enter the interval in seconds (e.g., 60 for 1 minute): ").strip())
    
    # Instantiate CandleViewer with user input
    candle_viewer = CandleViewer(symbol=symbol, interval_sec=interval_sec)
