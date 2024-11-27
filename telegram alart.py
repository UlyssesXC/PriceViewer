import ccxt
import time
import pandas as pd
import pytz
import requests

# Telegram bot details
bot_token = ''  # Replace with your bot's token
chat_ids = []      # Replace with your Telegram chat ID

# Function to send Telegram message to multiple chat IDs
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    for chat_id in chat_ids:
        payload = {
            "chat_id": chat_id,
            "text": message
        }
        requests.post(url, json=payload)

# Initialize the OKX exchange
exchange = ccxt.okx({
    'enableRateLimit': True,  # Rate limiting to avoid hitting API limits
})

# Define monitoring parameters for each timeframe
timeframes = {
    '1m': {'window_length': 14, 'volume_multiplier': 5, 'style': '*'},     # Least prominent
    '5m': {'window_length': 14, 'volume_multiplier': 5, 'style': '**'},    # Moderate visibility
    '15m': {'window_length': 14, 'volume_multiplier': 5, 'style': '***'},  # Most prominent
}
local_timezone = pytz.timezone('Canada/Eastern')

# Store rolling data and RSI history for each symbol and timeframe
rolling_data = {tf: {} for tf in timeframes}
rsi_history = {tf: {} for tf in timeframes}

while True:
    # Fetch all perpetual contract tickers
    all_tickers = exchange.load_markets()
    swap_tickers = {symbol: market for symbol, market in all_tickers.items() if market['type'] == 'swap' and market['quote'] == 'USDT'}
    symbols = list(swap_tickers.keys())[:100]  # Get top 100 USDT perpetual contracts by symbol

    # Monitor each symbol in multiple timeframes
    for symbol in symbols:
        for timeframe, params in timeframes.items():
            try:
                # Fetch the latest candles for the timeframe
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=15)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                
                # Calculate the latest datetime separately
                latest_row = df.iloc[-1]
                latest_datetime = pd.to_datetime(latest_row['timestamp'], unit='ms', utc=True).tz_convert(local_timezone)

                # Initialize rolling data for each symbol in each timeframe if it doesn’t exist
                if symbol not in rolling_data[timeframe]:
                    rolling_data[timeframe][symbol] = df['close'].tolist()[-params['window_length']-1:]
                else:
                    rolling_data[timeframe][symbol].append(latest_row['close'])
                    rolling_data[timeframe][symbol] = rolling_data[timeframe][symbol][-params['window_length']-1:]

                # Calculate RSI if we have enough data
                if len(rolling_data[timeframe][symbol]) >= params['window_length'] + 1:
                    closes = pd.Series(rolling_data[timeframe][symbol])
                    change = closes.diff()
                    gain = change.where(change > 0, 0).rolling(window=params['window_length']).mean()
                    loss = -change.where(change < 0, 0).rolling(window=params['window_length']).mean()
                    rs = gain / loss
                    rsi = 100 - (100 / (1 + rs.iloc[-1]))

                    # Calculate RSI slope based on history
                    previous_rsi = rsi_history[timeframe].get(symbol, rsi)
                    rsi_slope = rsi - previous_rsi
                    rsi_history[timeframe][symbol] = rsi

                    # Buy/Sell logic based on RSI and volume conditions
                    volume_avg_20 = df['volume'].rolling(window=20).mean().iloc[-1]
                    if (rsi > 50 and rsi_slope > 0) and (latest_row['volume'] > params['volume_multiplier'] * volume_avg_20):
                        message = (f"{params['style']}{latest_datetime} | {timeframe.upper()} BUY SIGNAL for {symbol} | "
                                   f"O: {latest_row['open']}, H: {latest_row['high']}, L: {latest_row['low']}, "
                                   f"C: {latest_row['close']}, V: {latest_row['volume']}, RSI: {rsi:.2f}, "
                                   f"RSI Slope: {rsi_slope:.2f}{params['style']}")
                        send_telegram_message(message)

                    elif rsi < 30 and rsi_slope < 0:
                        message = (f"{params['style']}{latest_datetime} | {timeframe.upper()} SELL SIGNAL for {symbol} | "
                                   f"O: {latest_row['open']}, H: {latest_row['high']}, L: {latest_row['low']}, "
                                   f"C: {latest_row['close']}, V: {latest_row['volume']}, RSI: {rsi:.2f}, "
                                   f"RSI Slope: {rsi_slope:.2f}{params['style']}")
                        send_telegram_message(message)

            except Exception as e:
                print(f"Error processing {symbol} in {timeframe} timeframe: {e}")

    # Wait for 1 minute before the next scan
    print("Waiting for 1 minute before the next scan...")
    time.sleep(60)