"""
Risk Manager
Handles position sizing, risk limits, and portfolio management
"""

import logging


class RiskManager:
    """Manage trading risk and position sizing"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Load risk parameters
        risk_config = config['risk_management']
        self.max_position_size = risk_config['max_position_size']
        self.max_positions = risk_config['max_positions']
        self.stop_loss_percent = risk_config['stop_loss_percent']
        self.take_profit_percent = risk_config['take_profit_percent']
        self.risk_per_trade_percent = risk_config['risk_per_trade_percent']
        self.max_daily_loss = risk_config['max_daily_loss']
        
        # Track daily statistics
        self.daily_pnl = 0
        self.open_positions_count = 0
    
    def calculate_position_size(self, entry_price, stop_loss_price, account_balance=10000):
        """
        Calculate position size based on risk parameters
        
        Args:
            entry_price: Entry price
            stop_loss_price: Stop loss price
            account_balance: Account balance (for percentage-based sizing)
            
        Returns:
            Position size in base currency
        """
        # Calculate risk per trade in dollars
        risk_amount = account_balance * (self.risk_per_trade_percent / 100)
        
        # Calculate price risk
        price_risk = abs(entry_price - stop_loss_price)
        
        if price_risk == 0:
            self.logger.warning("Zero price risk, using max position size")
            return self.max_position_size / entry_price
        
        # Calculate position size
        position_size = risk_amount / price_risk
        
        # Apply max position size limit
        max_size_units = self.max_position_size / entry_price
        position_size = min(position_size, max_size_units)
        
        return position_size
    
    def can_open_position(self):
        """Check if we can open a new position"""
        if self.open_positions_count >= self.max_positions:
            self.logger.debug(f"Max positions reached: {self.open_positions_count}/{self.max_positions}")
            return False
        
        # Check daily loss limit
        if abs(self.daily_pnl) >= self.max_daily_loss:
            self.logger.warning(f"Daily loss limit reached: ${self.daily_pnl:.2f}")
            return False
        
        return True
    
    def check_risk_limits(self, pair, action, size):
        """
        Verify trade meets risk requirements
        
        Args:
            pair: Trading pair
            action: buy/sell
            size: Position size
            
        Returns:
            bool: True if trade is allowed
        """
        # Check position count
        if not self.can_open_position():
            return False
        
        # Add more risk checks as needed
        return True
    
    def update_daily_pnl(self, pnl):
        """Update daily P&L tracking"""
        self.daily_pnl += pnl
        
        if abs(self.daily_pnl) >= self.max_daily_loss:
            self.logger.critical(f"⚠️  DAILY LOSS LIMIT REACHED: ${self.daily_pnl:.2f}")
    
    def increment_positions(self):
        """Increment open positions counter"""
        self.open_positions_count += 1
    
    def decrement_positions(self):
        """Decrement open positions counter"""
        self.open_positions_count = max(0, self.open_positions_count - 1)
    
    def reset_daily_stats(self):
        """Reset daily statistics (call at start of each trading day)"""
        self.daily_pnl = 0
        self.logger.info("Daily statistics reset")
    
    def get_risk_summary(self):
        """Get current risk metrics"""
        return {
            'daily_pnl': self.daily_pnl,
            'open_positions': self.open_positions_count,
            'max_positions': self.max_positions,
            'remaining_daily_loss': self.max_daily_loss - abs(self.daily_pnl),
            'max_position_size': self.max_position_size
        }
