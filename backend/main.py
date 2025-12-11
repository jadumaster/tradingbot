"""
Advanced Trading Bot - Main Entry Point
Supports Forex and Cryptocurrency Trading with Multiple Strategies
"""

import sys
import os
import yaml
import logging
import threading
import time
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engines.data_feed import DataFeed
from engines.order_executor import OrderExecutor
from engines.risk_manager import RiskManager
from engines.backtester import Backtester
from strategies.rsi_strategy import RSIStrategy
from strategies.macd_strategy import MACDStrategy
from strategies.bollinger_strategy import BollingerStrategy
from strategies.ma_crossover import MACrossoverStrategy
from database.db_manager import DatabaseManager
from utils.notifications import NotificationManager
from utils.helpers import setup_logging, load_config

class TradingBot:
    """Main Trading Bot Controller"""
    
    def __init__(self, config_path='config.yaml'):
        """Initialize the trading bot"""
        self.config = load_config(config_path)
        self.logger = setup_logging(self.config)
        self.running = False
        
        # Initialize components
        self.db_manager = DatabaseManager(self.config)
        self.risk_manager = RiskManager(self.config)
        self.notification_manager = NotificationManager(self.config)
        self.data_feed = DataFeed(self.config)
        self.order_executor = OrderExecutor(self.config, self.db_manager)
        
        # Initialize strategies
        self.strategies = self._initialize_strategies()
        
        self.logger.info("=" * 60)
        self.logger.info("🚀 TRADING BOT INITIALIZED")
        self.logger.info(f"Mode: {self.config['trading_mode'].upper()}")
        self.logger.info(f"Active Strategies: {len(self.strategies)}")
        self.logger.info("=" * 60)
    
    def _initialize_strategies(self):
        """Load and initialize enabled trading strategies"""
        strategies = []
        
        for strategy_config in self.config['strategies']:
            if not strategy_config.get('enabled', False):
                continue
                
            strategy_name = strategy_config['name']
            
            if strategy_name == 'RSI_Mean_Reversion':
                strategy = RSIStrategy(strategy_config)
            elif strategy_name == 'MACD_Trend_Following':
                strategy = MACDStrategy(strategy_config)
            elif strategy_name == 'Bollinger_Bands':
                strategy = BollingerStrategy(strategy_config)
            elif strategy_name == 'MA_Crossover':
                strategy = MACrossoverStrategy(strategy_config)
            else:
                self.logger.warning(f"Unknown strategy: {strategy_name}")
                continue
            
            strategies.append(strategy)
            self.logger.info(f"✓ Loaded strategy: {strategy_name}")
        
        return strategies
    
    def run_backtest(self):
        """Run backtesting on historical data"""
        self.logger.info("📊 Starting Backtesting Mode...")
        
        backtester = Backtester(self.config, self.strategies)
        results = backtester.run()
        
        self.logger.info("=" * 60)
        self.logger.info("📈 BACKTEST RESULTS")
        self.logger.info(f"Total Trades: {results['total_trades']}")
        self.logger.info(f"Winning Trades: {results['winning_trades']}")
        self.logger.info(f"Win Rate: {results['win_rate']:.2f}%")
        self.logger.info(f"Total Profit/Loss: ${results['total_pnl']:.2f}")
        self.logger.info(f"Max Drawdown: {results['max_drawdown']:.2f}%")
        self.logger.info(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        self.logger.info("=" * 60)
        
        return results
    
    def run_live(self):
        """Run the bot in live trading mode"""
        self.logger.info("🔴 Starting LIVE Trading Mode...")
        self.running = True
        
        # Send startup notification
        self.notification_manager.send_notification(
            "🚀 Trading Bot Started",
            f"Mode: {self.config['trading_mode']}\n"
            f"Strategies: {len(self.strategies)}"
        )
        
        try:
            while self.running:
                self._trading_loop()
                time.sleep(60)  # Run every minute
                
        except KeyboardInterrupt:
            self.logger.info("⚠️  Shutdown signal received...")
            self.shutdown()
    
    def _trading_loop(self):
        """Main trading logic loop"""
        try:
            # Get all trading pairs
            all_pairs = []
            if self.config['markets']['crypto']['enabled']:
                all_pairs.extend(self.config['markets']['crypto']['pairs'])
            if self.config['markets']['forex']['enabled']:
                all_pairs.extend(self.config['markets']['forex']['pairs'])
            
            for pair in all_pairs:
                # Check if we can open new positions
                if not self.risk_manager.can_open_position():
                    self.logger.debug("Max positions reached, skipping new signals")
                    continue
                
                # Get market data
                market_data = self.data_feed.get_market_data(pair)
                
                if market_data is None:
                    continue
                
                # Run all strategies
                for strategy in self.strategies:
                    signal = strategy.generate_signal(market_data)
                    
                    if signal['action'] != 'hold':
                        self._process_signal(pair, signal, market_data)
                
                # Check existing positions for stop-loss/take-profit
                self._manage_positions(pair, market_data)
                
        except Exception as e:
            self.logger.error(f"Error in trading loop: {e}", exc_info=True)
    
    def _process_signal(self, pair, signal, market_data):
        """Process a trading signal"""
        current_price = market_data['close'].iloc[-1]
        
        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(
            current_price,
            signal.get('stop_loss', current_price * 0.98)
        )
        
        if position_size == 0:
            return
        
        # Check risk limits
        if not self.risk_manager.check_risk_limits(pair, signal['action'], position_size):
            self.logger.warning(f"Risk limits exceeded for {pair}")
            return
        
        # Execute the trade
        order = self.order_executor.execute_order(
            pair=pair,
            action=signal['action'],
            size=position_size,
            price=current_price,
            strategy=signal['strategy'],
            stop_loss=signal.get('stop_loss'),
            take_profit=signal.get('take_profit')
        )
        
        if order:
            # Log and notify
            self.logger.info(
                f"🎯 {signal['action'].upper()} {pair} @ ${current_price:.2f} "
                f"| Size: {position_size:.4f} | Strategy: {signal['strategy']}"
            )
            
            self.notification_manager.send_notification(
                f"🎯 New {signal['action'].upper()} Signal",
                f"Pair: {pair}\n"
                f"Price: ${current_price:.2f}\n"
                f"Size: {position_size:.4f}\n"
                f"Strategy: {signal['strategy']}"
            )
    
    def _manage_positions(self, pair, market_data):
        """Manage existing positions (stop-loss, take-profit)"""
        positions = self.db_manager.get_open_positions(pair)
        current_price = market_data['close'].iloc[-1]
        
        for position in positions:
            # Check stop-loss
            if position['stop_loss'] and current_price <= position['stop_loss']:
                self.order_executor.close_position(position, current_price, 'stop_loss')
                self.logger.info(f"🛑 Stop-Loss triggered for {pair} @ ${current_price:.2f}")
                
            # Check take-profit
            elif position['take_profit'] and current_price >= position['take_profit']:
                self.order_executor.close_position(position, current_price, 'take_profit')
                self.logger.info(f"💰 Take-Profit triggered for {pair} @ ${current_price:.2f}")
    
    def shutdown(self):
        """Gracefully shutdown the bot"""
        self.running = False
        
        # Close all positions if in paper mode
        if self.config['trading_mode'] == 'paper':
            self.logger.info("Closing all open positions...")
            self.order_executor.close_all_positions()
        
        self.notification_manager.send_notification(
            "⏹️  Trading Bot Stopped",
            "Bot has been shut down gracefully."
        )
        
        self.logger.info("✓ Trading Bot shut down successfully")


def main():
    """Main entry point"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║          🤖 ADVANCED TRADING BOT v1.0                   ║
    ║                                                          ║
    ║          Forex & Crypto Automated Trading System         ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Load configuration
    config_path = Path(__file__).parent.parent / 'config.yaml'
    
    bot = TradingBot(config_path)
    
    # Check if user wants to run backtest or live trading
    print("\n📋 Select Mode:")
    print("1. 🔴 Live Trading")
    print("2. 📊 Backtesting")
    print("3. 📈 Run Web Dashboard")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            confirmation = input(
                f"\n⚠️  You are about to start {bot.config['trading_mode'].upper()} trading.\n"
                "Continue? (yes/no): "
            ).strip().lower()
            
            if confirmation == 'yes':
                bot.run_live()
            else:
                print("✗ Cancelled")
                
        elif choice == '2':
            bot.run_backtest()
            
        elif choice == '3':
            print("🌐 Starting Web Dashboard...")
            from web_server import start_dashboard
            start_dashboard(bot.config)
            
        else:
            print("✗ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        bot.shutdown()


if __name__ == "__main__":
    main()
