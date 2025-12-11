"""
Bollinger Bands Breakout Strategy
Trade breakouts from volatility bands
"""

import pandas as pd
import ta


class BollingerStrategy:
    """Bollinger Bands breakout strategy"""
    
    def __init__(self, config):
        self.name = "Bollinger Bands Breakout"
        self.timeframe = config.get('timeframe', '30m')
        self.period = config.get('period', 20)
        self.std_dev = config.get('std_dev', 2)
    
    def generate_signal(self, market_data):
        """
        Generate trading signal based on Bollinger Bands
        
        Args:
            market_data: DataFrame with OHLCV data
            
        Returns:
            dict: Signal with action, strategy name, and levels
        """
        if len(market_data) < self.period + 1:
            return {'action': 'hold', 'strategy': self.name}
        
        # Calculate Bollinger Bands
        bb_indicator = ta.volatility.BollingerBands(
            market_data['close'],
            window=self.period,
            window_dev=self.std_dev
        )
        
        upper_band = bb_indicator.bollinger_hband()
        lower_band = bb_indicator.bollinger_lband()
        middle_band = bb_indicator.bollinger_mavg()
        
        current_price = market_data['close'].iloc[-1]
        previous_price = market_data['close'].iloc[-2]
        
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        current_middle = middle_band.iloc[-1]
        
        # Buy signal: Price breaks below lower band (oversold, potential reversal)
        if previous_price >= current_lower and current_price < current_lower:
            return {
                'action': 'buy',
                'strategy': self.name,
                'upper_band': current_upper,
                'lower_band': current_lower,
                'middle_band': current_middle,
                'stop_loss': current_price * 0.98,
                'take_profit': current_middle  # Target: middle band
            }
        
        # Sell signal: Price breaks above upper band (overbought, potential reversal)
        elif previous_price <= current_upper and current_price > current_upper:
            return {
                'action': 'sell',
                'strategy': self.name,
                'upper_band': current_upper,
                'lower_band': current_lower,
                'middle_band': current_middle,
                'stop_loss': current_price * 1.02,
                'take_profit': current_middle  # Target: middle band
            }
        
        return {
            'action': 'hold',
            'strategy': self.name,
            'upper_band': current_upper,
            'lower_band': current_lower,
            'middle_band': current_middle
        }
    
    def get_indicators(self, market_data):
        """Get indicator values for display"""
        if len(market_data) < self.period + 1:
            return {}
        
        bb_indicator = ta.volatility.BollingerBands(
            market_data['close'],
            window=self.period,
            window_dev=self.std_dev
        )
        
        return {
            'upper_band': bb_indicator.bollinger_hband().iloc[-1],
            'lower_band': bb_indicator.bollinger_lband().iloc[-1],
            'middle_band': bb_indicator.bollinger_mavg().iloc[-1],
            'bandwidth': bb_indicator.bollinger_wband().iloc[-1]
        }
