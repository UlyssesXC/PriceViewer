from candleviewer import CandleViewer
import ccxt
import pandas as pd

# Fetch data before user input.
def get_top_10_pairs_by_volume(exchange_name='binance'):
    # TODO: ERROR HANDLE e.g. throw error if no networking connection.
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
