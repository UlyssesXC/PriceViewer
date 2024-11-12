import ccxt
import mplfinance as mpf
import pandas as pd
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt

class CandleViewer:
    def __init__(self, exchange_name='binance', symbol='BTC/USDT', interval='1m', kline_limit=100):
        self.symbol = symbol
        self.interval = interval
        self.kline_limit = kline_limit

        # 初始化交易所
        self.exchange = getattr(ccxt, exchange_name)()
        
        # 获取初始K线数据并转换为DataFrame
        self.data = self.fetch_initial_klines()
        
        # 创建图表
        self.fig, self.ax = plt.subplots()
        
        # 启动动画更新
        self.ani = FuncAnimation(self.fig, self.update, interval=1000)
        plt.show()

    def fetch_initial_klines(self):
        """获取前100根K线数据并转换为DataFrame格式"""
        ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe=self.interval, limit=self.kline_limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df

    def fetch_latest_kline(self):
        """获取最新一根K线数据并转换为DataFrame格式"""
        ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe=self.interval, limit=1)
        if ohlcv:
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        else:
            return None  # 返回None以表示未获取到数据

    def update(self, frame):
        """更新图表数据"""
        latest_df = self.fetch_latest_kline()
        
        if latest_df is not None:  # 检查是否获取到有效数据
            self.data = pd.concat([self.data, latest_df])
            if len(self.data) > self.kline_limit:
                self.data = self.data.iloc[1:]
            
            # 清空ax并重新绘制蜡烛图
            self.ax.clear()
            mpf.plot(self.data, type='candle', style='charles', ax=self.ax, show_nontrading=False)

            # 添加标题和标签
            self.ax.set_title(f'{self.symbol} 实时价格')
            self.ax.set_xlabel('时间')
            self.ax.set_ylabel('价格 (USDT)')

# 实例化CandleViewer
candle_viewer = CandleViewer()
