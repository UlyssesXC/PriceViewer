# UWO ECE9013 Group 5 Project

## Project Description

Real-time candlestick chart viewer for stock/cryptocurrency pairs using `ccxt`, `mplfinance`, and `matplotlib`. 

It enables users to visualize live market data with automatic candlestick chart with some indicators.

## File Descriptions

- `candleviewer.py`:
  - CandleViewer class location
  - Fetches candlestick data from a specified exchange and symbol
  - Displays real-time data in a candlestick chart
  - Calculates and displays Relative Strength Index (RSI) values (TBD)
  - Customizable interval and kline limit settings
  - Animated chart updates
- `telegram alart.py`:
  - Interface for pushing alert to telegram based on charts data

## Todolist

- [ ] Including stock data
- [ ] RSI calculation
- [ ] Telegram alert  interface/class (for fun)
- [ ] Other indicators
