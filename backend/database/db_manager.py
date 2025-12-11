"""
Database Manager
Handle trade storage and retrieval
"""

import logging
import sqlite3
import json
from datetime import datetime
from pathlib import Path


class DatabaseManager:
    """Manage trade database operations"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        db_config = config['database']
        self.db_type = db_config['type']
        
        if self.db_type == 'sqlite':
            self.db_path = Path(__file__).parent.parent.parent / db_config['sqlite_path']
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_sqlite()
        else:
            self.logger.warning("MongoDB not implemented yet, using SQLite")
            self.db_path = Path(__file__).parent.parent.parent / 'data' / 'trades.db'
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_sqlite()
    
    def _init_sqlite(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Create trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                pair TEXT NOT NULL,
                action TEXT NOT NULL,
                size REAL NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                current_price REAL,
                stop_loss REAL,
                take_profit REAL,
                strategy TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                close_timestamp TEXT,
                pnl REAL,
                pnl_percent REAL,
                close_reason TEXT
            )
        ''')
        
        # Create performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                total_trades INTEGER,
                winning_trades INTEGER,
                total_pnl REAL,
                balance REAL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"✓ Database initialized: {self.db_path}")
    
    def save_trade(self, trade):
        """Save a trade to database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trades (
                    id, pair, action, size, entry_price, current_price,
                    stop_loss, take_profit, strategy, status, timestamp, pnl, pnl_percent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade['id'],
                trade['pair'],
                trade['action'],
                trade['size'],
                trade['entry_price'],
                trade['current_price'],
                trade.get('stop_loss'),
                trade.get('take_profit'),
                trade['strategy'],
                trade['status'],
                trade['timestamp'].isoformat(),
                trade.get('pnl', 0),
                trade.get('pnl_percent', 0)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error saving trade: {e}", exc_info=True)
    
    def update_trade(self, trade):
        """Update an existing trade"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE trades SET
                    exit_price = ?,
                    current_price = ?,
                    status = ?,
                    close_timestamp = ?,
                    pnl = ?,
                    pnl_percent = ?,
                    close_reason = ?
                WHERE id = ?
            ''', (
                trade.get('exit_price'),
                trade.get('current_price'),
                trade['status'],
                trade.get('close_timestamp').isoformat() if trade.get('close_timestamp') else None,
                trade.get('pnl', 0),
                trade.get('pnl_percent', 0),
                trade.get('close_reason'),
                trade['id']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error updating trade: {e}", exc_info=True)
    
    def get_open_positions(self, pair=None):
        """Get all open positions, optionally filtered by pair"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if pair:
                cursor.execute('SELECT * FROM trades WHERE status = ? AND pair = ?', ('open', pair))
            else:
                cursor.execute('SELECT * FROM trades WHERE status = ?', ('open',))
            
            rows = cursor.fetchall()
            conn.close()
            
            positions = []
            for row in rows:
                positions.append(dict(row))
            
            return positions
            
        except Exception as e:
            self.logger.error(f"Error fetching open positions: {e}")
            return []
    
    def get_all_open_positions(self):
        """Get all open positions"""
        return self.get_open_positions()
    
    def get_trade_history(self, limit=100):
        """Get trade history"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT * FROM trades ORDER BY timestamp DESC LIMIT ?',
                (limit,)
            )
            
            rows = cursor.fetchall()
            conn.close()
            
            trades = []
            for row in rows:
                trades.append(dict(row))
            
            return trades
            
        except Exception as e:
            self.logger.error(f"Error fetching trade history: {e}")
            return []
    
    def get_performance_stats(self):
        """Get overall performance statistics"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get total stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                    SUM(pnl) as total_pnl,
                    AVG(CASE WHEN pnl > 0 THEN pnl ELSE NULL END) as avg_win,
                    AVG(CASE WHEN pnl < 0 THEN pnl ELSE NULL END) as avg_loss
                FROM trades
                WHERE status = 'closed'
            ''')
            
            row = cursor.fetchone()
            conn.close()
            
            total_trades = row[0] or 0
            winning_trades = row[1] or 0
            total_pnl = row[2] or 0
            avg_win = row[3] or 0
            avg_loss = row[4] or 0
            
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': total_trades - winning_trades,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'avg_win': avg_win,
                'avg_loss': avg_loss
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching performance stats: {e}")
            return {}
    
    def clear_database(self):
        """Clear all trades (use with caution!)"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM trades')
            cursor.execute('DELETE FROM performance')
            
            conn.commit()
            conn.close()
            
            self.logger.info("✓ Database cleared")
            
        except Exception as e:
            self.logger.error(f"Error clearing database: {e}")
