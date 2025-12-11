"""
RSI Mean Reversion Strategy
Buy when oversold, sell when overbought
"""

import pandas as pd
import ta


class RSIStrategy:
    """RSI-based mean reversion trading strategy"""
    
    def __init__(self, config):
        self.name = "RSI Mean Reversion"
        self.timeframe = config.get('timeframe', '15m')
        self.rsi_period = config.get('rsi_period', 14)
        self.oversold = config.get('oversold', 30)
        self.overbought = config.get('overbought', 70)
    
    def generate_signal(self, market_data):
        """
        Generate trading signal based on RSI
        
        Args:
            market_data: DataFrame with OHLCV data
            
        Returns:
            dict: Signal with action, strategy name, and levels
        """
        if len(market_data) < self.rsi_period + 1:
            return {'action': 'hold', 'strategy': self.name}
        
        # Calculate RSI
        rsi = ta.momentum.RSIIndicator(
            market_data['close'], 
            window=self.rsi_period
        ).rsi()
        
        current_rsi = rsi.iloc[-1]
        previous_rsi = rsi.iloc[-2]
        current_price = market_data['close'].iloc[-1]
        
        # Buy signal: RSI crosses above oversold level
        if previous_rsi <= self.oversold and current_rsi > self.oversold:
            return {
                'action': 'buy',
                'strategy': self.name,
                'rsi': current_rsi,
                'stop_loss': current_price * 0.98,  # 2% stop loss
                'take_profit': current_price * 1.04  # 4% take profit
            }
        
        # Sell signal: RSI crosses below overbought level
        elif previous_rsi >= self.overbought and current_rsi < self.overbought:
            return {
                'action': 'sell',
                'strategy': self.name,
                'rsi': current_rsi,
                'stop_loss': current_price * 1.02,
                'take_profit': current_price * 0.96
            }
        
        return {'action': 'hold', 'strategy': self.name, 'rsi': current_rsi}
    
    def get_indicators(self, market_data):
        """Get indicator values for display"""
        if len(market_data) < self.rsi_period + 1:
            return {}
        
        rsi = ta.momentum.RSIIndicator(
            market_data['close'], 
            window=self.rsi_period
        ).rsi()
        
        return {
            'rsi': rsi.iloc[-1],
            'oversold_level': self.oversold,
            'overbought_level': self.overbought
        }
