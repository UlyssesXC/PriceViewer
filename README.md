# UWO ECE9013 Group 5 Project

## Project Description

Real-time candlestick chart viewer for stock/cryptocurrency pairs using `ccxt`, `mplfinance`, and `matplotlib`. 

It enables users to visualize live market data with automatic candlestick chart with some indicators.

## File Descriptions

- `candleviewer.py`:
  - CandleViewer class location
  - Fetches candlestick data from a specified exchange and symbol
  - Displays real-time data in a candlestick chart
  - Calculates and displays MA values    
  - Customizable interval and kline limit settings
  - Animated chart updates
- `main.py`:  
  - Get top10 pairs by volume for user to choose
  - Location of main function.

## Code Structure
![8901537ba430d94c4fbfdb1f07cc023](https://github.com/user-attachments/assets/dab1a1ac-3f47-41f2-afdb-b68e951418c8)

## Refer Link
CCXT error hierarchy: https://github.com/ccxt/ccxt/blob/master/python/ccxt/base/errors.py
mplfinance: https://github.com/matplotlib/mplfinance
