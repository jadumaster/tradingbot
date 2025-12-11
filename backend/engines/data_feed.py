"""
Data Feed Engine
Handles real-time and historical market data from multiple sources
"""

import ccxt
import pandas as pd
import logging
from datetime import datetime, timedelta

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False


class DataFeed:
    """Unified data feed for crypto and forex markets"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.exchanges = {}
        self.mt5_initialized = False
        
        # Initialize crypto exchanges
        if config['markets']['crypto']['enabled']:
            self._initialize_crypto()
        
        # Initialize forex broker
        if config['markets']['forex']['enabled']:
            self._initialize_forex()
    
    def _initialize_crypto(self):
        """Initialize cryptocurrency exchange connections"""
        try:
            exchange_name = self.config['markets']['crypto']['exchange']
            exchange_class = getattr(ccxt, exchange_name)
            
            self.exchanges['crypto'] = exchange_class({
                'apiKey': self.config['markets']['crypto'].get('api_key', ''),
                'secret': self.config['markets']['crypto'].get('api_secret', ''),
                'enableRateLimit': True,
            })
            
            self.logger.info(f"✓ Connected to {exchange_name} exchange")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize crypto exchange: {e}")
    
    def _initialize_forex(self):
        """Initialize forex broker connection (MetaTrader5 or OANDA)"""
        broker = self.config['markets']['forex'].get('broker', 'oanda')
        
        if broker == 'mt5' and MT5_AVAILABLE:
            try:
                if mt5.initialize():
                    self.mt5_initialized = True
                    self.logger.info("✓ Connected to MetaTrader5")
                else:
                    self.logger.error("Failed to initialize MT5")
            except Exception as e:
                self.logger.error(f"MT5 initialization error: {e}")
        else:
            self.logger.info(f"Forex broker: {broker} (API implementation needed)")
    
    def get_market_data(self, symbol, timeframe='1h', limit=100):
        """
        Get market data for a symbol
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT' or 'EUR/USD')
            timeframe: Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles to fetch
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Determine if crypto or forex
            if '/' in symbol and symbol.split('/')[1] in ['USDT', 'USD', 'BTC', 'ETH']:
                return self._get_crypto_data(symbol, timeframe, limit)
            else:
                return self._get_forex_data(symbol, timeframe, limit)
                
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def _get_crypto_data(self, symbol, timeframe, limit):
        """Fetch cryptocurrency data"""
        if 'crypto' not in self.exchanges:
            self.logger.error("Crypto exchange not initialized")
            return None
        
        try:
            exchange = self.exchanges['crypto']
            
            # Fetch OHLCV data
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            # Convert to DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching crypto data for {symbol}: {e}")
            return None
    
    def _get_forex_data(self, symbol, timeframe, limit):
        """Fetch forex data from MT5 or broker API"""
        
        if self.mt5_initialized:
            return self._get_mt5_data(symbol, timeframe, limit)
        else:
            # Fallback: Generate sample data for demo purposes
            self.logger.warning(f"Using sample data for {symbol} (forex broker not connected)")
            return self._generate_sample_data(limit)
    
    def _get_mt5_data(self, symbol, timeframe, limit):
        """Fetch data from MetaTrader5"""
        try:
            # Map timeframe to MT5 constant
            timeframe_map = {
                '1m': mt5.TIMEFRAME_M1,
                '5m': mt5.TIMEFRAME_M5,
                '15m': mt5.TIMEFRAME_M15,
                '30m': mt5.TIMEFRAME_M30,
                '1h': mt5.TIMEFRAME_H1,
                '4h': mt5.TIMEFRAME_H4,
                '1d': mt5.TIMEFRAME_D1,
            }
            
            mt5_timeframe = timeframe_map.get(timeframe, mt5.TIMEFRAME_H1)
            
            # Fetch rates
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, limit)
            
            if rates is None:
                raise Exception(f"Failed to fetch MT5 data for {symbol}")
            
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['timestamp'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('timestamp', inplace=True)
            df = df[['open', 'high', 'low', 'close', 'tick_volume']]
            df.rename(columns={'tick_volume': 'volume'}, inplace=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching MT5 data: {e}")
            return None
    
    def _generate_sample_data(self, limit):
        """Generate sample OHLCV data for testing"""
        import numpy as np
        
        # Generate realistic-looking price data
        dates = pd.date_range(end=datetime.now(), periods=limit, freq='1H')
        base_price = 100
        
        # Random walk
        returns = np.random.normal(0, 0.02, limit)
        prices = base_price * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            'open': prices * (1 + np.random.uniform(-0.01, 0.01, limit)),
            'high': prices * (1 + np.random.uniform(0, 0.02, limit)),
            'low': prices * (1 + np.random.uniform(-0.02, 0, limit)),
            'close': prices,
            'volume': np.random.uniform(1000, 10000, limit)
        }, index=dates)
        
        return df
    
    def get_current_price(self, symbol):
        """Get current market price"""
        try:
            if 'crypto' in self.exchanges:
                ticker = self.exchanges['crypto'].fetch_ticker(symbol)
                return ticker['last']
            else:
                # Use last close from sample data
                df = self.get_market_data(symbol, limit=1)
                return df['close'].iloc[-1] if df is not None else None
                
        except Exception as e:
            self.logger.error(f"Error fetching current price for {symbol}: {e}")
            return None
    
    def __del__(self):
        """Cleanup on destruction"""
        if self.mt5_initialized:
            mt5.shutdown()
