"""
Moving Average Crossover Strategy
Classic trend identification using MA crosses
"""

import pandas as pd
import ta


class MACrossoverStrategy:
    """Moving Average Crossover strategy"""
    
    def __init__(self, config):
        self.name = "MA Crossover"
        self.timeframe = config.get('timeframe', '4h')
        self.fast_ma = config.get('fast_ma', 50)
        self.slow_ma = config.get('slow_ma', 200)
    
    def generate_signal(self, market_data):
        """
        Generate trading signal based on MA crossover
        
        Args:
            market_data: DataFrame with OHLCV data
            
        Returns:
            dict: Signal with action, strategy name, and levels
        """
        if len(market_data) < self.slow_ma + 1:
            return {'action': 'hold', 'strategy': self.name}
        
        # Calculate moving averages
        fast_sma = ta.trend.SMAIndicator(
            market_data['close'], 
            window=self.fast_ma
        ).sma_indicator()
        
        slow_sma = ta.trend.SMAIndicator(
            market_data['close'], 
            window=self.slow_ma
        ).sma_indicator()
        
        current_fast = fast_sma.iloc[-1]
        current_slow = slow_sma.iloc[-1]
        previous_fast = fast_sma.iloc[-2]
        previous_slow = slow_sma.iloc[-2]
        
        current_price = market_data['close'].iloc[-1]
        
        # Buy signal: Fast MA crosses above Slow MA (Golden Cross)
        if previous_fast <= previous_slow and current_fast > current_slow:
            return {
                'action': 'buy',
                'strategy': self.name,
                'fast_ma': current_fast,
                'slow_ma': current_slow,
                'signal_type': 'Golden Cross',
                'stop_loss': current_slow,  # Use slow MA as stop
                'take_profit': current_price * 1.05
            }
        
        # Sell signal: Fast MA crosses below Slow MA (Death Cross)
        elif previous_fast >= previous_slow and current_fast < current_slow:
            return {
                'action': 'sell',
                'strategy': self.name,
                'fast_ma': current_fast,
                'slow_ma': current_slow,
                'signal_type': 'Death Cross',
                'stop_loss': current_slow,
                'take_profit': current_price * 0.95
            }
        
        return {
            'action': 'hold',
            'strategy': self.name,
            'fast_ma': current_fast,
            'slow_ma': current_slow
        }
    
    def get_indicators(self, market_data):
        """Get indicator values for display"""
        if len(market_data) < self.slow_ma + 1:
            return {}
        
        fast_sma = ta.trend.SMAIndicator(
            market_data['close'], 
            window=self.fast_ma
        ).sma_indicator()
        
        slow_sma = ta.trend.SMAIndicator(
            market_data['close'], 
            window=self.slow_ma
        ).sma_indicator()
        
        return {
            'fast_ma': fast_sma.iloc[-1],
            'slow_ma': slow_sma.iloc[-1],
            'distance': ((fast_sma.iloc[-1] - slow_sma.iloc[-1]) / slow_sma.iloc[-1]) * 100
        }
