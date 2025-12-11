"""
Backtesting Engine
Test strategies on historical data
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class Backtester:
    """Backtest trading strategies on historical data"""
    
    def __init__(self, config, strategies):
        self.config = config
        self.strategies = strategies
        self.logger = logging.getLogger(__name__)
        
        # Backtesting parameters
        bt_config = config['backtesting']
        self.start_date = bt_config['start_date']
        self.end_date = bt_config['end_date']
        self.initial_balance = bt_config['initial_balance']
        
        # Results tracking
        self.trades = []
        self.balance = self.initial_balance
        self.equity_curve = []
    
    def run(self):
        """Run backtesting simulation"""
        self.logger.info("=" * 60)
        self.logger.info("Starting Backtesting")
        self.logger.info(f"Period: {self.start_date} to {self.end_date}")
        self.logger.info(f"Initial Balance: ${self.initial_balance}")
        self.logger.info("=" * 60)
        
        # Get all trading pairs
        all_pairs = []
        if self.config['markets']['crypto']['enabled']:
            all_pairs.extend(self.config['markets']['crypto']['pairs'])
        if self.config['markets']['forex']['enabled']:
            all_pairs.extend(self.config['markets']['forex']['pairs'])
        
        # Run backtest for each pair
        for pair in all_pairs:
            self._backtest_pair(pair)
        
        # Calculate results
        results = self._calculate_results()
        
        return results
    
    def _backtest_pair(self, pair):
        """Backtest strategies on a single pair"""
        self.logger.info(f"Backtesting {pair}...")
        
        # In a real scenario, fetch historical data
        # For now, generate sample data
        historical_data = self._fetch_historical_data(pair)
        
        if historical_data is None or len(historical_data) < 200:
            self.logger.warning(f"Insufficient data for {pair}")
            return
        
        # Simulate trading day by day
        for i in range(200, len(historical_data)):
            # Get data window
            data_window = historical_data.iloc[:i]
            
            # Run each strategy
            for strategy in self.strategies:
                signal = strategy.generate_signal(data_window)
                
                if signal['action'] != 'hold':
                    self._execute_backtest_trade(
                        pair,
                        signal,
                        historical_data.iloc[i]['close']
                    )
    
    def _fetch_historical_data(self, pair):
        """Fetch or generate historical data"""
        # In production, fetch from data feed
        # For demo, generate sample data
        from engines.data_feed import DataFeed
        
        data_feed = DataFeed(self.config)
        data = data_feed.get_market_data(pair, timeframe='1d', limit=500)
        
        return data
    
    def _execute_backtest_trade(self, pair, signal, price):
        """Execute a trade in backtest"""
        # Simple backtesting logic
        risk_per_trade = self.balance * 0.01  # 1% risk
        
        # Calculate position size
        if signal.get('stop_loss'):
            price_risk = abs(price - signal['stop_loss'])
            position_size = risk_per_trade / price_risk if price_risk > 0 else 0
        else:
            position_size = risk_per_trade / (price * 0.02)  # Default 2% risk
        
        # Limit position size
        max_position_value = min(self.balance * 0.1, 1000)  # Max 10% of balance
        position_size = min(position_size, max_position_value / price)
        
        if position_size <= 0:
            return
        
        # Record trade
        trade = {
            'pair': pair,
            'action': signal['action'],
            'strategy': signal['strategy'],
            'entry_price': price,
            'size': position_size,
            'stop_loss': signal.get('stop_loss'),
            'take_profit': signal.get('take_profit'),
            'timestamp': datetime.now()
        }
        
        # Simulate exit (simplified)
        if signal.get('take_profit'):
            exit_price = signal['take_profit']
        elif signal.get('stop_loss'):
            # Random exit between stop and take profit
            exit_price = price * np.random.uniform(0.99, 1.03)
        else:
            exit_price = price * 1.02  # Default 2% profit
        
        # Calculate P&L
        if signal['action'] == 'buy':
            pnl = (exit_price - price) * position_size
        else:
            pnl = (price - exit_price) * position_size
        
        trade['exit_price'] = exit_price
        trade['pnl'] = pnl
        
        self.balance += pnl
        self.trades.append(trade)
        self.equity_curve.append(self.balance)
    
    def _calculate_results(self):
        """Calculate backtest performance metrics"""
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0
            }
        
        total_trades = len(self.trades)
        winning_trades = len([t for t in self.trades if t['pnl'] > 0])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        total_pnl = sum(t['pnl'] for t in self.trades)
        
        # Calculate max drawdown
        equity_curve = np.array(self.equity_curve)
        running_max = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - running_max) / running_max
        max_drawdown = abs(drawdown.min()) * 100 if len(drawdown) > 0 else 0
        
        # Calculate Sharpe ratio (simplified)
        returns = np.diff(equity_curve) / equity_curve[:-1] if len(equity_curve) > 1 else np.array([0])
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': total_trades - winning_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'final_balance': self.balance,
            'return_percent': ((self.balance - self.initial_balance) / self.initial_balance) * 100,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'avg_win': np.mean([t['pnl'] for t in self.trades if t['pnl'] > 0]) if winning_trades > 0 else 0,
            'avg_loss': np.mean([t['pnl'] for t in self.trades if t['pnl'] < 0]) if (total_trades - winning_trades) > 0 else 0
        }
