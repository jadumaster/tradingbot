"""
Helper Utilities
Common functions used throughout the bot
"""

import logging
import yaml
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama for Windows
init(autoreset=True)


def load_config(config_path='config.yaml'):
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to config file
        
    Returns:
        dict: Configuration dictionary
    """
    try:
        if isinstance(config_path, str):
            config_path = Path(config_path)
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        return config
        
    except Exception as e:
        print(f"Error loading config: {e}")
        raise


def setup_logging(config):
    """
    Setup logging configuration
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Logger instance
    """
    log_config = config.get('logging', {})
    log_level = log_config.get('level', 'INFO')
    log_file = log_config.get('file', 'logs/trading_bot.log')
    
    # Create logs directory
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Add color to console output
    logger = logging.getLogger()
    
    return logger


def format_currency(amount, symbol='$'):
    """Format currency with symbol"""
    return f"{symbol}{amount:,.2f}"


def format_percent(value, decimals=2):
    """Format percentage"""
    return f"{value:.{decimals}f}%"


def calculate_percentage_change(old_value, new_value):
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0
    return ((new_value - old_value) / old_value) * 100


def print_banner():
    """Print application banner"""
    banner = f"""
    {Fore.CYAN}╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║          🤖 ADVANCED TRADING BOT v1.0                   ║
    ║                                                          ║
    ║          Forex & Crypto Automated Trading System         ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(banner)


def print_trade_summary(trade):
    """Print formatted trade summary"""
    color = Fore.GREEN if trade.get('pnl', 0) > 0 else Fore.RED
    
    print(f"\n{color}{'='*60}")
    print(f"Trade ID: {trade['id']}")
    print(f"Pair: {trade['pair']}")
    print(f"Action: {trade['action'].upper()}")
    print(f"Entry Price: ${trade['entry_price']:.2f}")
    if trade.get('exit_price'):
        print(f"Exit Price: ${trade['exit_price']:.2f}")
        print(f"P&L: ${trade['pnl']:.2f} ({trade['pnl_percent']:.2f}%)")
    print(f"Strategy: {trade['strategy']}")
    print(f"{'='*60}{Style.RESET_ALL}\n")


def validate_config(config):
    """Validate configuration file"""
    required_keys = ['trading_mode', 'markets', 'strategies', 'risk_management']
    
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")
    
    # Validate trading mode
    if config['trading_mode'] not in ['paper', 'live']:
        raise ValueError("trading_mode must be 'paper' or 'live'")
    
    # Validate at least one market is enabled
    if not (config['markets']['crypto']['enabled'] or config['markets']['forex']['enabled']):
        raise ValueError("At least one market (crypto or forex) must be enabled")
    
    return True


def get_timeframe_minutes(timeframe):
    """Convert timeframe string to minutes"""
    timeframe_map = {
        '1m': 1,
        '5m': 5,
        '15m': 15,
        '30m': 30,
        '1h': 60,
        '4h': 240,
        '1d': 1440,
        '1w': 10080
    }
    return timeframe_map.get(timeframe, 60)


def safe_divide(numerator, denominator, default=0):
    """Safely divide two numbers"""
    try:
        return numerator / denominator if denominator != 0 else default
    except:
        return default
