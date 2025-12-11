"""
User Model
Handles user accounts, authentication, and subscriptions
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import enum

Base = declarative_base()


class SubscriptionTier(enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class User(Base):
    """User account model"""
    
    __tablename__ = 'users'
    
    # Primary Info
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    
    # Profile
    full_name = Column(String(120))
    phone = Column(String(20))
    country = Column(String(50))
    
    # Account Status
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime)
    
    # Subscription
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    subscription_start = Column(DateTime)
    subscription_end = Column(DateTime)
    stripe_customer_id = Column(String(100))
    stripe_subscription_id = Column(String(100))
    
    # Trading Settings
    api_key_crypto = Column(String(256))  # Encrypted
    api_secret_crypto = Column(String(256))  # Encrypted
    api_key_forex = Column(String(256))  # Encrypted
    api_secret_forex = Column(String(256))  # Encrypted
    
    # Account Balance (for paper trading)
    paper_balance = Column(Float, default=10000.0)
    
    # Risk Management
    max_position_size = Column(Float, default=1000.0)
    max_positions = Column(Integer, default=3)
    daily_loss_limit = Column(Float, default=5.0)
    
    # Trading Status
    auto_trading_enabled = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    def __init__(self, username, email, password, **kwargs):
        self.username = username
        self.email = email
        self.set_password(password)
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def is_subscription_active(self):
        """Check if subscription is active"""
        if self.subscription_tier == SubscriptionTier.FREE:
            return True
        if not self.subscription_end:
            return False
        return datetime.utcnow() < self.subscription_end
    
    def get_subscription_limits(self):
        """Get limits based on subscription tier"""
        limits = {
            SubscriptionTier.FREE: {
                'max_strategies': 2,
                'max_pairs': 3,
                'max_positions': 2,
                'max_daily_trades': 10,
                'backtesting_days': 30,
                'real_trading': False,
                'telegram_alerts': False,
                'priority_support': False
            },
            SubscriptionTier.PRO: {
                'max_strategies': 10,
                'max_pairs': 20,
                'max_positions': 10,
                'max_daily_trades': 100,
                'backtesting_days': 365,
                'real_trading': True,
                'telegram_alerts': True,
                'priority_support': False
            },
            SubscriptionTier.ENTERPRISE: {
                'max_strategies': -1,  # Unlimited
                'max_pairs': -1,
                'max_positions': -1,
                'max_daily_trades': -1,
                'backtesting_days': -1,
                'real_trading': True,
                'telegram_alerts': True,
                'priority_support': True
            }
        }
        return limits.get(self.subscription_tier, limits[SubscriptionTier.FREE])
    
    def to_dict(self, include_sensitive=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'subscription_tier': self.subscription_tier.value if self.subscription_tier else 'free',
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'is_verified': self.is_verified,
            'auto_trading_enabled': self.auto_trading_enabled,
            'paper_balance': self.paper_balance,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'subscription_active': self.is_subscription_active(),
            'limits': self.get_subscription_limits()
        }
        
        if include_sensitive:
            data['api_key_crypto'] = self.api_key_crypto
            data['api_key_forex'] = self.api_key_forex
        
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'


class APIKey(Base):
    """User API Keys for exchanges"""
    
    __tablename__ = 'api_keys'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    exchange_name = Column(String(50), nullable=False)  # binance, oanda, etc.
    api_key = Column(String(256), nullable=False)  # Encrypted
    api_secret = Column(String(256), nullable=False)  # Encrypted
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<APIKey {self.exchange_name} for User {self.user_id}>'


class UserSession(Base):
    """User sessions for tracking logins"""
    
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    token = Column(String(256), unique=True, nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(String(256))
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    def __init__(self, user_id, token, **kwargs):
        self.user_id = user_id
        self.token = token
        self.expires_at = datetime.utcnow() + timedelta(days=7)
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def is_expired(self):
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f'<Session for User {self.user_id}>'
