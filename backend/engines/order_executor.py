"""
Order Executor Engine
Handles trade execution and position management
"""

import logging
import uuid
from datetime import datetime


class OrderExecutor:
    """Execute and manage trading orders"""
    
    def __init__(self, config, db_manager):
        self.config = config
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.trading_mode = config['trading_mode']
    
    def execute_order(self, pair, action, size, price, strategy, stop_loss=None, take_profit=None):
        """
        Execute a trading order
        
        Args:
            pair: Trading pair
            action: 'buy' or 'sell'
            size: Position size
            price: Entry price
            strategy: Strategy name
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            Order object or None
        """
        try:
            order = {
                'id': str(uuid.uuid4()),
                'pair': pair,
                'action': action,
                'size': size,
                'entry_price': price,
                'current_price': price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': strategy,
                'status': 'open',
                'timestamp': datetime.now(),
                'pnl': 0,
                'pnl_percent': 0
            }
            
            if self.trading_mode == 'paper':
                # Paper trading - simulate order
                self.db_manager.save_trade(order)
                self.logger.info(f"📝 Paper trade executed: {action.upper()} {size:.4f} {pair} @ ${price:.2f}")
                
            elif self.trading_mode == 'live':
                # Live trading - execute real order
                # TODO: Implement actual order execution via exchange API
                self.logger.warning("Live trading not yet implemented - using paper mode")
                self.db_manager.save_trade(order)
            
            return order
            
        except Exception as e:
            self.logger.error(f"Error executing order: {e}", exc_info=True)
            return None
    
    def close_position(self, position, exit_price, reason='manual'):
        """
        Close an open position
        
        Args:
            position: Position object
            exit_price: Exit price
            reason: Closure reason (manual, stop_loss, take_profit)
        """
        try:
            # Calculate P&L
            if position['action'] == 'buy':
                pnl = (exit_price - position['entry_price']) * position['size']
                pnl_percent = ((exit_price - position['entry_price']) / position['entry_price']) * 100
            else:  # sell
                pnl = (position['entry_price'] - exit_price) * position['size']
                pnl_percent = ((position['entry_price'] - exit_price) / position['entry_price']) * 100
            
            # Update position
            position['status'] = 'closed'
            position['exit_price'] = exit_price
            position['close_timestamp'] = datetime.now()
            position['pnl'] = pnl
            position['pnl_percent'] = pnl_percent
            position['close_reason'] = reason
            
            self.db_manager.update_trade(position)
            
            self.logger.info(
                f"✅ Position closed: {position['pair']} | "
                f"P&L: ${pnl:.2f} ({pnl_percent:.2f}%) | "
                f"Reason: {reason}"
            )
            
            return position
            
        except Exception as e:
            self.logger.error(f"Error closing position: {e}", exc_info=True)
            return None
    
    def close_all_positions(self):
        """Close all open positions"""
        open_positions = self.db_manager.get_all_open_positions()
        
        for position in open_positions:
            # Use current price as exit price
            # In real scenario, fetch actual market price
            exit_price = position['current_price']
            self.close_position(position, exit_price, 'shutdown')
        
        self.logger.info(f"Closed {len(open_positions)} open positions")
    
    def update_position_prices(self, pair, current_price):
        """Update current prices for open positions"""
        positions = self.db_manager.get_open_positions(pair)
        
        for position in positions:
            # Calculate unrealized P&L
            if position['action'] == 'buy':
                pnl = (current_price - position['entry_price']) * position['size']
                pnl_percent = ((current_price - position['entry_price']) / position['entry_price']) * 100
            else:
                pnl = (position['entry_price'] - current_price) * position['size']
                pnl_percent = ((position['entry_price'] - current_price) / position['entry_price']) * 100
            
            position['current_price'] = current_price
            position['pnl'] = pnl
            position['pnl_percent'] = pnl_percent
            
            self.db_manager.update_trade(position)
