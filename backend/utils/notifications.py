"""
Notification Manager
Send alerts via Telegram and Email
"""

import logging
from datetime import datetime

try:
    from telegram import Bot
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False


class NotificationManager:
    """Manage trading notifications"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize Telegram
        self.telegram_enabled = config['notifications']['telegram']['enabled']
        if self.telegram_enabled and TELEGRAM_AVAILABLE:
            self._init_telegram()
        elif self.telegram_enabled and not TELEGRAM_AVAILABLE:
            self.logger.warning("Telegram notifications enabled but telegram package not installed")
            self.telegram_enabled = False
        
        # Email notifications (TODO)
        self.email_enabled = config['notifications']['email']['enabled']
    
    def _init_telegram(self):
        """Initialize Telegram bot"""
        try:
            bot_token = self.config['notifications']['telegram']['bot_token']
            self.chat_id = self.config['notifications']['telegram']['chat_id']
            self.bot = Bot(token=bot_token)
            self.logger.info("✓ Telegram notifications enabled")
        except Exception as e:
            self.logger.error(f"Failed to initialize Telegram: {e}")
            self.telegram_enabled = False
    
    def send_notification(self, title, message):
        """
        Send a notification
        
        Args:
            title: Notification title
            message: Notification message
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"**{title}**\n{message}\n\n_{timestamp}_"
        
        # Log locally
        self.logger.info(f"📬 Notification: {title} - {message}")
        
        # Send via Telegram
        if self.telegram_enabled:
            self._send_telegram(full_message)
        
        # Send via Email
        if self.email_enabled:
            self._send_email(title, message)
    
    def _send_telegram(self, message):
        """Send message via Telegram"""
        try:
            self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            self.logger.error(f"Telegram send error: {e}")
    
    def _send_email(self, subject, body):
        """Send email notification (TODO)"""
        # TODO: Implement email sending
        self.logger.debug("Email notifications not yet implemented")
    
    def send_trade_alert(self, trade):
        """Send alert for a new trade"""
        title = f"🎯 New {trade['action'].upper()} Trade"
        message = (
            f"Pair: {trade['pair']}\n"
            f"Price: ${trade['entry_price']:.2f}\n"
            f"Size: {trade['size']:.4f}\n"
            f"Strategy: {trade['strategy']}"
        )
        self.send_notification(title, message)
    
    def send_close_alert(self, trade):
        """Send alert for a closed trade"""
        emoji = "💰" if trade['pnl'] > 0 else "📉"
        title = f"{emoji} Trade Closed"
        message = (
            f"Pair: {trade['pair']}\n"
            f"Entry: ${trade['entry_price']:.2f}\n"
            f"Exit: ${trade['exit_price']:.2f}\n"
            f"P&L: ${trade['pnl']:.2f} ({trade['pnl_percent']:.2f}%)\n"
            f"Reason: {trade.get('close_reason', 'manual')}"
        )
        self.send_notification(title, message)
    
    def send_error_alert(self, error_message):
        """Send alert for errors"""
        self.send_notification("⚠️ Trading Bot Error", error_message)
    
    def send_daily_summary(self, stats):
        """Send daily performance summary"""
        title = "📊 Daily Trading Summary"
        message = (
            f"Total Trades: {stats.get('total_trades', 0)}\n"
            f"Win Rate: {stats.get('win_rate', 0):.1f}%\n"
            f"Total P&L: ${stats.get('total_pnl', 0):.2f}\n"
            f"Open Positions: {stats.get('open_positions', 0)}"
        )
        self.send_notification(title, message)
