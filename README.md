<<<<<<< HEAD
# 🤖 Advanced Trading Bot

> **Professional Automated Trading System for Forex & Cryptocurrency Markets**

A powerful, production-ready trading bot with multiple strategies, risk management, backtesting capabilities, and a stunning real-time dashboard.

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

### 🎯 Trading Capabilities
- ✅ **Multi-Market Support**: Trade both Crypto and Forex
- ✅ **Multiple Strategies**: RSI, MACD, Bollinger Bands, MA Crossover
- ✅ **Paper & Live Trading**: Test strategies safely before going live
- ✅ **Risk Management**: Stop-loss, take-profit, position sizing
- ✅ **Backtesting Engine**: Test strategies on historical data

### 📊 Dashboard & Analytics
- ✅ **Real-Time Dashboard**: Beautiful web interface with live charts
- ✅ **Performance Metrics**: Track P&L, win rate, Sharpe ratio
- ✅ **Position Management**: Monitor active and closed positions
- ✅ **Market Watch**: Live price feeds for all trading pairs

### 🔔 Notifications & Alerts
- ✅ **Telegram Integration**: Get trade alerts on your phone
- ✅ **Email Notifications**: Receive daily summaries
- ✅ **Custom Alerts**: Configure alerts for specific events

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **pip** package manager
- Windows OS (for MetaTrader5 integration)

### Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure settings**:
   Edit `config.yaml` with your API keys and preferences

4. **Run the bot**:
   ```bash
   cd backend
   python main.py
   ```

### First Run

On first launch, you'll see a menu:

```
1. 🔴 Live Trading
2. 📊 Backtesting
3. 📈 Run Web Dashboard
```

**Recommended**: Start with option 2 (Backtesting) to test your strategies!

---

## 📁 Project Structure

```
Trading Bot/
├── backend/
│   ├── main.py                 # Main entry point
│   ├── web_server.py           # Dashboard server
│   ├── strategies/             # Trading strategies
│   │   ├── rsi_strategy.py
│   │   ├── macd_strategy.py
│   │   ├── bollinger_strategy.py
│   │   └── ma_crossover.py
│   ├── engines/
│   │   ├── data_feed.py        # Market data fetching
│   │   ├── order_executor.py   # Order execution
│   │   ├── risk_manager.py     # Risk management
│   │   └── backtester.py       # Backtesting engine
│   ├── database/
│   │   └── db_manager.py       # Database operations
│   └── utils/
│       ├── notifications.py    # Alerts & notifications
│       └── helpers.py          # Utility functions
├── frontend/
│   ├── index.html              # Dashboard UI
│   ├── styles.css              # Premium styling
│   └── app.js                  # Frontend logic
├── data/                       # Database storage
├── logs/                       # Log files
├── config.yaml                 # Configuration file
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## ⚙️ Configuration

Edit `config.yaml` to customize:

### Trading Mode
```yaml
trading_mode: paper  # Use 'paper' for simulation, 'live' for real trading
```

### API Keys

**Crypto (Binance example)**:
```yaml
markets:
  crypto:
    enabled: true
    exchange: binance
    api_key: YOUR_BINANCE_API_KEY
    api_secret: YOUR_BINANCE_SECRET
```

**Forex (OANDA example)**:
```yaml
markets:
  forex:
    enabled: true
    broker: oanda
    api_key: YOUR_OANDA_API_KEY
    api_secret: YOUR_OANDA_SECRET
```

### Strategies

Enable/disable strategies:
```yaml
strategies:
  - name: RSI_Mean_Reversion
    enabled: true
    rsi_period: 14
    oversold: 30
    overbought: 70
```

### Risk Management

```yaml
risk_management:
  max_position_size: 1000      # Max USD per position
  max_positions: 3             # Max concurrent positions
  stop_loss_percent: 2.0       # 2% stop loss
  take_profit_percent: 4.0     # 4% take profit
```

---

## 📊 Trading Strategies

### 1. **RSI Mean Reversion**
- **Logic**: Buy when oversold (RSI < 30), sell when overbought (RSI > 70)
- **Best For**: Range-bound markets
- **Timeframe**: 15m - 1h

### 2. **MACD Trend Following**
- **Logic**: Buy on bullish crossover, sell on bearish crossover
- **Best For**: Trending markets
- **Timeframe**: 1h - 4h

### 3. **Bollinger Bands**
- **Logic**: Trade breakouts from volatility bands
- **Best For**: High volatility periods
- **Timeframe**: 30m - 1h

### 4. **MA Crossover**
- **Logic**: Golden Cross (buy) / Death Cross (sell)
- **Best For**: Long-term trends
- **Timeframe**: 4h - 1d

---

## 🖥️ Dashboard

Access the web dashboard at: **http://localhost:8080**

### Features:
- 📈 **Real-time equity curve**
- 💰 **Performance metrics** (P&L, win rate, Sharpe ratio)
- 🔥 **Active positions** with live P&L
- 📜 **Trade history**
- 🎯 **Strategy performance breakdown**
- 📡 **Live market data**

---

## 📱 Telegram Notifications

1. **Create a Telegram bot**:
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Send `/newbot` and follow instructions
   - Copy your bot token

2. **Get your Chat ID**:
   - Message [@userinfobot](https://t.me/userinfobot)
   - Copy your Chat ID

3. **Update config.yaml**:
   ```yaml
   notifications:
     telegram:
       enabled: true
       bot_token: YOUR_BOT_TOKEN
       chat_id: YOUR_CHAT_ID
   ```

---

## 🧪 Backtesting

Test strategies before risking real money:

```bash
python main.py
# Select option 2 (Backtesting)
```

You'll see results like:
```
📈 BACKTEST RESULTS
Total Trades: 45
Winning Trades: 28
Win Rate: 62.22%
Total Profit/Loss: $1,234.56
Max Drawdown: 8.45%
Sharpe Ratio: 1.85
```

---

## 🔐 Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Enable IP whitelisting** on exchange/broker
4. **Start with paper trading** to test everything
5. **Use separate API keys** for trading bot (with restricted permissions)

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'ccxt'`
- **Fix**: Run `pip install -r requirements.txt`

**Issue**: MetaTrader5 not connecting
- **Fix**: Ensure MT5 is installed and terminal is running

**Issue**: Dashboard not loading
- **Fix**: Check if port 8080 is available, try a different port in config

**Issue**: No trades being executed
- **Fix**: Check if strategies are enabled in config.yaml

---

## 📈 Performance Tips

1. **Start Conservative**: Begin with small position sizes
2. **Diversify Strategies**: Use multiple strategies for different market conditions
3. **Monitor Daily**: Check dashboard daily for anomalies
4. **Adjust Parameters**: Fine-tune strategy parameters based on backtest results
5. **Risk Management**: Never risk more than 1-2% per trade

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests
pytest

# Format code
black backend/
```

---

## 📄 License

This project is licensed under the MIT License.

---

## ⚠️ Disclaimer

**Trading involves substantial risk of loss. This software is provided for educational purposes only.**

- Past performance does not guarantee future results
- Never trade with money you can't afford to lose
- Always test strategies thoroughly in paper mode first
- Author is not responsible for any financial losses

---

## 📞 Support

- **Documentation**: [See Wiki](#)
- **Issues**: [GitHub Issues](#)
- **Discord**: [Join Community](#)

---

## 🎯 Roadmap

- [ ] Machine Learning strategies (LSTM, Random Forest)
- [ ] Multi-timeframe analysis
- [ ] Portfolio optimization
- [ ] Cloud deployment support
- [ ] Mobile app (iOS/Android)
- [ ] Social trading features

---

## 💎 Premium Features (Coming Soon)

- Advanced AI-powered strategies
- Custom strategy builder (no code)
- Priority support
- Exclusive Discord channel

---

**Built with ❤️ for automated trading enthusiasts**

*Happy Trading! 🚀*
=======
# tradingbot
>>>>>>> 82b95b891d616c31af01d6cce696a06b5c7b532b
