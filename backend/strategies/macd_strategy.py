"""
MACD Trend Following Strategy
Follow momentum shifts and trend changes
"""

import pandas as pd
import ta


class MACDStrategy:
    """MACD-based trend following strategy"""
    
    def __init__(self, config):
        self.name = "MACD Trend Following"
        self.timeframe = config.get('timeframe', '1h')
        self.fast_period = config.get('fast_period', 12)
        self.slow_period = config.get('slow_period', 26)
        self.signal_period = config.get('signal_period', 9)
    
    def generate_signal(self, market_data):
        """
        Generate trading signal based on MACD crossover
        
        Args:
            market_data: DataFrame with OHLCV data
            
        Returns:
            dict: Signal with action, strategy name, and levels
        """
        if len(market_data) < self.slow_period + self.signal_period:
            return {'action': 'hold', 'strategy': self.name}
        
        # Calculate MACD
        macd_indicator = ta.trend.MACD(
            market_data['close'],
            window_fast=self.fast_period,
            window_slow=self.slow_period,
            window_sign=self.signal_period
        )
        
        macd = macd_indicator.macd()
        signal = macd_indicator.macd_signal()
        histogram = macd_indicator.macd_diff()
        
        current_histogram = histogram.iloc[-1]
        previous_histogram = histogram.iloc[-2]
        current_price = market_data['close'].iloc[-1]
        
        # Buy signal: MACD crosses above signal line (histogram crosses above 0)
        if previous_histogram <= 0 and current_histogram > 0:
            return {
                'action': 'buy',
                'strategy': self.name,
                'macd': macd.iloc[-1],
                'signal': signal.iloc[-1],
                'histogram': current_histogram,
                'stop_loss': current_price * 0.98,
                'take_profit': current_price * 1.04
            }
        
        # Sell signal: MACD crosses below signal line (histogram crosses below 0)
        elif previous_histogram >= 0 and current_histogram < 0:
            return {
                'action': 'sell',
                'strategy': self.name,
                'macd': macd.iloc[-1],
                'signal': signal.iloc[-1],
                'histogram': current_histogram,
                'stop_loss': current_price * 1.02,
                'take_profit': current_price * 0.96
            }
        
        return {
            'action': 'hold',
            'strategy': self.name,
            'macd': macd.iloc[-1],
            'signal': signal.iloc[-1],
            'histogram': current_histogram
        }
    
    def get_indicators(self, market_data):
        """Get indicator values for display"""
        if len(market_data) < self.slow_period + self.signal_period:
            return {}
        
        macd_indicator = ta.trend.MACD(
            market_data['close'],
            window_fast=self.fast_period,
            window_slow=self.slow_period,
            window_sign=self.signal_period
        )
        
        return {
            'macd': macd_indicator.macd().iloc[-1],
            'signal': macd_indicator.macd_signal().iloc[-1],
            'histogram': macd_indicator.macd_diff().iloc[-1]
        }
