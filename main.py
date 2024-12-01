from candleviewer import CandleViewer
import ccxt
import pandas as pd

# Fetch data before user input.
def get_top_10_pairs_by_volume(exchange_name='binance'): #coinbase crypto exchange crypto currency
    """Get the top 10 trading pairs by volume"""
    try:
        print("Fetching top 10 trading pairs by volume...")
        exchange = getattr(ccxt, exchange_name)()

        # Fetch all tickers
        markets = exchange.fetch_tickers()
        print("Fetched trading pairs data successfully.")

        # Extract symbol and volume information
        data = []
        for symbol, ticker in markets.items():
            if 'quoteVolume' in ticker:
                data.append({
                    'symbol': symbol,
                    'volume': ticker['quoteVolume']
                })

        # Convert to DataFrame for sorting
        df = pd.DataFrame(data)
        # Sort by volume and select the top 10
        top_10 = df.sort_values(by='volume', ascending=False).head(10) #sory by volume

        return top_10['symbol'].tolist()

    except ccxt.NetworkError as e:
        print(f"Network error occurred while fetching trading pairs: {e}")
        raise
    except ccxt.BaseError as e:
        print(f"Exchange API error occurred: {e}")
        raise
    except Exception as e:
        print(f"An unknown error occurred: {e}")
        raise

if __name__ == "__main__":
    try:
        top_10_pairs = get_top_10_pairs_by_volume()
    except Exception as e:
        print(f"Error fetching top 10 trading pairs: {e}")
        exit()
    while True: #main loop
        try:

            print("\nTop 10 trading pairs on Binance recently:")
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
            candle_viewer = CandleViewer(symbol=symbol, interval_sec=interval_sec, ma_periods=(25,50,)) # create candle viewer instance
            break
        except Exception as e:
            print(f"Please try again.")
