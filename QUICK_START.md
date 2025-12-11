# 🚀 QUICK SETUP GUIDE

Welcome to the Advanced Trading Bot! Follow these steps to get started in minutes.

---

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies

Open Command Prompt or PowerShell in the project folder and run:

```bash
pip install -r requirements.txt
```

Wait for all packages to install (this may take 2-3 minutes).

---

### Step 2: Test the Dashboard

Run the quick start script:

```bash
start.bat
```

Or manually:

```bash
cd backend
python web_server.py
```

Your browser will automatically open to `http://localhost:8080`

You should see the beautiful trading dashboard! 🎨

---

### Step 3: Run a Backtest

Let's test the strategies on historical data:

```bash
cd backend
python main.py
```

Select option `2` (Backtesting) when prompted.

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

### Step 4: Configure for Your Needs

Edit `config.yaml`:

**For Crypto Trading (Binance)**:

1. Create API keys at [Binance](https://www.binance.com/en/my/settings/api-management)
2. Update config:
   ```yaml
   markets:
     crypto:
       enabled: true
       exchange: binance
       api_key: YOUR_API_KEY_HERE
       api_secret: YOUR_SECRET_HERE
   ```

**For Forex Trading (OANDA)**:

1. Create account at [OANDA](https://www.oanda.com/)
2. Get API credentials
3. Update config:
   ```yaml
   markets:
     forex:
       enabled: true
       broker: oanda
       api_key: YOUR_API_KEY_HERE
       api_secret: YOUR_SECRET_HERE
   ```

---

### Step 5: Start Paper Trading

Paper trading = **NO REAL MONEY** - perfect for testing!

```bash
cd backend
python main.py
```

Select option `1` (Live Trading)

The bot will:
- ✅ Connect to exchanges
- ✅ Analyze markets in real-time
- ✅ Execute simulated trades
- ✅ Send you notifications

**Monitor progress on the dashboard**: http://localhost:8080

---

## 📋 Checklist Before Live Trading

Before risking real money, make sure:

- [ ] ✅ Backtesting shows profitable results
- [ ] ✅ Paper trading works correctly for at least 1 week
- [ ] ✅ You understand each strategy
- [ ] ✅ Risk management is configured (stop-loss, position limits)
- [ ] ✅ Notifications are working
- [ ] ✅ You've read the full README.md

---

## 🎯 Strategy Selection Guide

Choose strategies based on market conditions:

| Market Condition | Recommended Strategies |
|-----------------|----------------------|
| **Trending Up/Down** | MACD, MA Crossover |
| **Range-Bound** | RSI Mean Reversion |
| **High Volatility** | Bollinger Bands |
| **Uncertain** | Mix of all (diversify) |

---

## ⚙️ Recommended Settings for Beginners

```yaml
trading_mode: paper  # ALWAYS start with paper!

risk_management:
  max_position_size: 100      # Small positions
  max_positions: 2            # Only 2 at a time
  stop_loss_percent: 2.0      # Tight stop-loss
  take_profit_percent: 4.0    # 2:1 risk/reward
  max_daily_loss: 3.0         # Stop if lose 3%

strategies:
  - name: RSI_Mean_Reversion
    enabled: true             # Start with 1-2 strategies
    
  - name: MACD_Trend_Following
    enabled: true
    
  - name: Bollinger_Bands
    enabled: false            # Disable complex ones first
```

---

## 🔄 Daily Workflow

1. **Morning** (5 min):
   - Check dashboard for overnight trades
   - Review performance metrics
   - Check notifications

2. **Midday** (2 min):
   - Quick dashboard check
   - Ensure bot is running

3. **Evening** (10 min):
   - Review all trades
   - Analyze strategy performance
   - Adjust settings if needed

---

## 🆘 Common Issues & Solutions

### "Module not found" error
```bash
pip install -r requirements.txt
```

### Dashboard won't load
- Check if port 8080 is free
- Try: http://127.0.0.1:8080 instead

### No trades being executed
- Verify strategies are `enabled: true` in config
- Check market data is updating
- Ensure API keys are correct

### Bot crashes
- Check `logs/trading_bot.log` for errors
- Verify Python version is 3.8+

---

## 📱 Enable Telegram Alerts (Optional)

1. Open Telegram and search for `@BotFather`
2. Send: `/newbot`
3. Follow instructions to create bot
4. Copy the **token** you receive
5. Search for `@userinfobot`
6. Send any message to get your **Chat ID**
7. Update `config.yaml`:

```yaml
notifications:
  telegram:
    enabled: true
    bot_token: "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
    chat_id: "987654321"
```

8. Restart bot and send test message!

---

## 📊 Interpreting Results

### Win Rate
- **> 60%**: Excellent! 🎉
- **50-60%**: Good, profitable with proper R:R
- **< 50%**: Needs optimization

### Sharpe Ratio
- **> 2.0**: Outstanding
- **1.0-2.0**: Good
- **< 1.0**: Risky

### Max Drawdown
- **< 10%**: Excellent risk management
- **10-20%**: Acceptable
- **> 20%**: Too risky, adjust settings

---

## 🎓 Next Steps

1. ✅ Complete this setup
2. 📚 Read full `README.md`
3. 🧪 Run backtests on different timeframes
4. 📝 Keep a trading journal
5. 🎯 Optimize one strategy at a time
6. 💰 Only go live when consistently profitable in paper mode

---

## 💡 Pro Tips

1. **Start Small**: Begin with minimum position sizes
2. **Diversify**: Use multiple strategies and pairs
3. **Be Patient**: Don't expect overnight success
4. **Keep Learning**: Markets change, adapt your strategies
5. **Risk Management**: This is MORE important than the strategy itself!

---

## 📞 Need Help?

- 📖 Full docs: See `README.md`
- 🐛 Found a bug? Check logs folder
- 💬 Questions? Review the code comments
- 🎯 Want to customize? All code is well-documented

---

**Remember**: This is a powerful tool, but **YOU** are in control. 

Always prioritize learning and risk management over profits.

**Good luck, and happy trading! 🚀📈**

---

*Last updated: 2024-12-12*
