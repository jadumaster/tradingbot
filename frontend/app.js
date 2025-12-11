/**
 * ADVANCED TRADING BOT - DASHBOARD JAVASCRIPT
 * Real-time updates, charts, and interactions
 */

// === GLOBAL STATE ===
let botState = {
    running: false,
    mode: 'paper',
    balance: 10000,
    trades: [],
    openPositions: [],
    performance: {
        totalPnl: 0,
        winRate: 0,
        totalTrades: 0,
        sharpeRatio: 0
    }
};

let equityChart = null;

// === INITIALIZATION ===
document.addEventListener('DOMContentLoaded', () => {
    initializeCharts();
    initializeEventListeners();
    loadMockData();
    startDataRefresh();
    loadStrategies();
    loadMarketData();
});

// === CHART INITIALIZATION ===
function initializeCharts() {
    const ctx = document.getElementById('equityChart');

    equityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Account Balance',
                data: [],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(17, 24, 39, 0.9)',
                    titleColor: '#f9fafb',
                    bodyColor: '#9ca3af',
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false
                }
            },
            scales: {
                x: {
                    display: false,
                    grid: {
                        display: false
                    }
                },
                y: {
                    position: 'right',
                    ticks: {
                        color: '#6b7280',
                        callback: function (value) {
                            return '$' + value.toLocaleString();
                        }
                    },
                    grid: {
                        color: 'rgba(99, 102, 241, 0.1)',
                        drawBorder: false
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

// === EVENT LISTENERS ===
function initializeEventListeners() {
    // Start/Stop Button
    document.getElementById('startStopBtn').addEventListener('click', toggleBot);

    // Settings Modal
    document.getElementById('settingsBtn').addEventListener('click', openSettings);
    document.getElementById('closeSettingsBtn').addEventListener('click', closeSettings);
    document.getElementById('saveSettingsBtn').addEventListener('click', saveSettings);

    // Time Period Selector
    document.querySelectorAll('.time-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            updateChartPeriod(e.target.dataset.period);
        });
    });

    // Market Tabs
    document.querySelectorAll('.market-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            document.querySelectorAll('.market-tab').forEach(t => t.classList.remove('active'));
            e.target.classList.add('active');
            loadMarketData(e.target.dataset.market);
        });
    });
}

// === BOT CONTROL ===
function toggleBot() {
    const btn = document.getElementById('startStopBtn');
    const statusBadge = document.getElementById('botStatus');

    botState.running = !botState.running;

    if (botState.running) {
        btn.innerHTML = '⏸️ Stop Trading';
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-danger');
        statusBadge.innerHTML = '<span class="pulse"></span> Active';
        statusBadge.classList.add('active');

        showNotification('✅ Trading Bot Started', 'success');
    } else {
        btn.innerHTML = '▶️ Start Trading';
        btn.classList.remove('btn-danger');
        btn.classList.add('btn-primary');
        statusBadge.innerHTML = '⏸️ Paused';
        statusBadge.classList.remove('active');

        showNotification('⏸️ Trading Bot Stopped', 'warning');
    }
}

// === SETTINGS MODAL ===
function openSettings() {
    document.getElementById('settingsModal').classList.add('active');
}

function closeSettings() {
    document.getElementById('settingsModal').classList.remove('active');
}

function saveSettings() {
    const mode = document.getElementById('tradingModeSelect').value;
    const maxPositions = document.getElementById('maxPositions').value;
    const stopLoss = document.getElementById('stopLoss').value;
    const takeProfit = document.getElementById('takeProfit').value;

    // Update state
    botState.mode = mode;
    document.getElementById('tradingMode').textContent = mode.toUpperCase();

    showNotification('💾 Settings Saved Successfully', 'success');
    closeSettings();
}

// === DATA LOADING ===
function loadMockData() {
    // Generate mock equity curve
    const now = Date.now();
    const points = 50;
    const labels = [];
    const data = [];
    let balance = 10000;

    for (let i = 0; i < points; i++) {
        const date = new Date(now - (points - i) * 3600000);
        labels.push(date.toLocaleTimeString());

        // Random walk with slight upward bias
        balance += (Math.random() - 0.45) * 100;
        data.push(Math.round(balance * 100) / 100);
    }

    equityChart.data.labels = labels;
    equityChart.data.datasets[0].data = data;
    equityChart.update('none');

    // Update balance
    botState.balance = data[data.length - 1];
    updatePerformanceMetrics();
}

function updatePerformanceMetrics() {
    // Generate mock performance data
    const totalTrades = Math.floor(Math.random() * 50) + 10;
    const winningTrades = Math.floor(totalTrades * (0.55 + Math.random() * 0.15));
    const totalPnl = (botState.balance - 10000);
    const winRate = (winningTrades / totalTrades) * 100;
    const sharpeRatio = 1.2 + Math.random() * 0.8;

    // Update DOM
    document.getElementById('currentBalance').textContent = '$' + botState.balance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    document.getElementById('totalPnl').textContent = (totalPnl >= 0 ? '+' : '') + '$' + totalPnl.toLocaleString('en-US', { minimumFractionDigits: 2 });
    document.getElementById('pnlChange').textContent = (totalPnl >= 0 ? '+' : '') + ((totalPnl / 10000) * 100).toFixed(2) + '%';
    document.getElementById('winRate').textContent = winRate.toFixed(1) + '%';
    document.getElementById('winRateDetail').textContent = `${winningTrades}/${totalTrades} trades`;
    document.getElementById('totalTrades').textContent = totalTrades;
    document.getElementById('tradesDetail').textContent = `${Math.floor(Math.random() * 3)} open positions`;
    document.getElementById('sharpeRatio').textContent = sharpeRatio.toFixed(2);

    // Update colors
    const pnlElement = document.getElementById('totalPnl');
    const changeElement = document.getElementById('pnlChange');

    if (totalPnl >= 0) {
        pnlElement.classList.add('profit');
        changeElement.classList.add('positive');
        changeElement.classList.remove('negative');
    } else {
        pnlElement.classList.remove('profit');
        changeElement.classList.remove('positive');
        changeElement.classList.add('negative');
    }
}

function loadActivePositions() {
    const container = document.getElementById('activePositions');
    const mockPositions = generateMockPositions();

    if (mockPositions.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                <p>No active positions</p>
            </div>
        `;
        return;
    }

    container.innerHTML = mockPositions.map(position => `
        <div class="position-card">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <div style="font-weight: 700; font-size: 1rem; margin-bottom: 0.25rem;">
                        ${position.pair}
                    </div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">
                        ${position.action.toUpperCase()} • ${position.strategy}
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-family: var(--font-mono); font-weight: 700; color: ${position.pnl >= 0 ? 'var(--accent-success)' : 'var(--accent-danger)'};">
                        ${position.pnl >= 0 ? '+' : ''}$${position.pnl.toFixed(2)}
                    </div>
                    <div style="font-size: 0.75rem; color: var(--text-tertiary);">
                        ${position.pnl >= 0 ? '+' : ''}${((position.pnl / position.entry) * 100).toFixed(2)}%
                    </div>
                </div>
            </div>
            <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid var(--border-color); font-size: 0.75rem; color: var(--text-tertiary);">
                Entry: $${position.entry.toFixed(2)} • Current: $${position.current.toFixed(2)}
            </div>
        </div>
    `).join('');

    document.getElementById('activeCount').textContent = mockPositions.length;
}

function loadRecentTrades() {
    const container = document.getElementById('recentTrades');
    const mockTrades = generateMockTrades();

    if (mockTrades.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📊</div>
                <p>No trades yet</p>
            </div>
        `;
        return;
    }

    container.innerHTML = mockTrades.map(trade => `
        <div class="trade-card">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <div style="font-weight: 700; font-size: 1rem; margin-bottom: 0.25rem;">
                        ${trade.pair}
                    </div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">
                        ${trade.action.toUpperCase()} • ${trade.time}
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-family: var(--font-mono); font-weight: 700; color: ${trade.pnl >= 0 ? 'var(--accent-success)' : 'var(--accent-danger)'};">
                        ${trade.pnl >= 0 ? '+' : ''}$${trade.pnl.toFixed(2)}
                    </div>
                    <div style="font-size: 0.75rem; color: var(--text-tertiary);">
                        ${trade.reason}
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// === STRATEGIES ===
function loadStrategies() {
    const strategies = [
        { name: 'RSI Mean Reversion', active: true, trades: 15, winRate: 66.7, pnl: 245.50 },
        { name: 'MACD Trend Following', active: true, trades: 12, winRate: 58.3, pnl: 189.30 },
        { name: 'Bollinger Bands', active: false, trades: 0, winRate: 0, pnl: 0 },
        { name: 'MA Crossover', active: true, trades: 8, winRate: 75.0, pnl: 312.80 }
    ];

    const container = document.getElementById('strategiesGrid');
    container.innerHTML = strategies.map(strategy => `
        <div class="strategy-card ${strategy.active ? 'active' : ''}">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                <h4 style="font-size: 1.125rem; font-weight: 700;">${strategy.name}</h4>
                <div style="width: 12px; height: 12px; border-radius: 50%; background: ${strategy.active ? 'var(--accent-success)' : 'var(--text-tertiary)'}"></div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; font-size: 0.875rem;">
                <div>
                    <div style="color: var(--text-tertiary); margin-bottom: 0.25rem;">Trades</div>
                    <div style="font-weight: 700; font-family: var(--font-mono);">${strategy.trades}</div>
                </div>
                <div>
                    <div style="color: var(--text-tertiary); margin-bottom: 0.25rem;">Win Rate</div>
                    <div style="font-weight: 700; font-family: var(--font-mono);">${strategy.winRate.toFixed(1)}%</div>
                </div>
                <div>
                    <div style="color: var(--text-tertiary); margin-bottom: 0.25rem;">P&L</div>
                    <div style="font-weight: 700; font-family: var(--font-mono); color: ${strategy.pnl >= 0 ? 'var(--accent-success)' : 'var(--accent-danger)'};">
                        ${strategy.pnl >= 0 ? '+' : ''}$${strategy.pnl.toFixed(2)}
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// === MARKET DATA ===
function loadMarketData(market = 'crypto') {
    const cryptoPairs = [
        { pair: 'BTC/USDT', price: 43250.50, change: 2.45 },
        { pair: 'ETH/USDT', price: 2280.75, change: -1.23 },
        { pair: 'SOL/USDT', price: 98.45, change: 5.67 }
    ];

    const forexPairs = [
        { pair: 'EUR/USD', price: 1.0845, change: 0.15 },
        { pair: 'GBP/USD', price: 1.2730, change: -0.08 },
        { pair: 'USD/JPY', price: 148.25, change: 0.32 }
    ];

    const pairs = market === 'crypto' ? cryptoPairs : forexPairs;
    const container = document.getElementById('marketGrid');

    container.innerHTML = pairs.map(pair => `
        <div style="background: var(--bg-tertiary); border: 1px solid var(--border-color); border-radius: var(--border-radius-sm); padding: 1rem;">
            <div style="font-weight: 700; margin-bottom: 0.5rem;">${pair.pair}</div>
            <div style="font-size: 1.25rem; font-family: var(--font-mono); font-weight: 700; margin-bottom: 0.25rem;">
                $${pair.price.toLocaleString()}
            </div>
            <div style="font-size: 0.875rem; font-weight: 600; color: ${pair.change >= 0 ? 'var(--accent-success)' : 'var(--accent-danger)'};">
                ${pair.change >= 0 ? '▲' : '▼'} ${Math.abs(pair.change)}%
            </div>
        </div>
    `).join('');
}

// === MOCK DATA GENERATORS ===
function generateMockPositions() {
    const pairs = ['BTC/USDT', 'ETH/USDT', 'EUR/USD'];
    const strategies = ['RSI Mean Reversion', 'MACD Trend Following', 'MA Crossover'];
    const positions = [];

    for (let i = 0; i < Math.floor(Math.random() * 3); i++) {
        const entry = 1000 + Math.random() * 500;
        const current = entry + (Math.random() - 0.5) * 100;
        positions.push({
            pair: pairs[Math.floor(Math.random() * pairs.length)],
            action: Math.random() > 0.5 ? 'buy' : 'sell',
            strategy: strategies[Math.floor(Math.random() * strategies.length)],
            entry: entry,
            current: current,
            pnl: current - entry
        });
    }

    return positions;
}

function generateMockTrades() {
    const pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'EUR/USD', 'GBP/USD'];
    const reasons = ['Take Profit', 'Stop Loss', 'Manual Close', 'Signal Exit'];
    const trades = [];

    for (let i = 0; i < 5; i++) {
        const pnl = (Math.random() - 0.3) * 100;
        trades.push({
            pair: pairs[Math.floor(Math.random() * pairs.length)],
            action: Math.random() > 0.5 ? 'buy' : 'sell',
            time: `${Math.floor(Math.random() * 12) + 1}h ago`,
            pnl: pnl,
            reason: reasons[Math.floor(Math.random() * reasons.length)]
        });
    }

    return trades;
}

// === NOTIFICATIONS ===
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? 'var(--accent-success)' : type === 'warning' ? 'var(--accent-warning)' : 'var(--accent-primary)'};
        color: white;
        border-radius: var(--border-radius-sm);
        box-shadow: var(--shadow-lg);
        z-index: 2000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// === AUTO REFRESH ===
function startDataRefresh() {
    setInterval(() => {
        if (botState.running) {
            updateLiveData();
        }
    }, 5000); // Refresh every 5 seconds
}

function updateLiveData() {
    // Simulate live updates
    const currentBalance = parseFloat(document.getElementById('currentBalance').textContent.replace(/[$,]/g, ''));
    const newBalance = currentBalance + (Math.random() - 0.48) * 50;

    // Update equity chart
    const newLabel = new Date().toLocaleTimeString();
    equityChart.data.labels.push(newLabel);
    equityChart.data.datasets[0].data.push(newBalance);

    // Keep only last 50 points
    if (equityChart.data.labels.length > 50) {
        equityChart.data.labels.shift();
        equityChart.data.datasets[0].data.shift();
    }

    equityChart.update('none');

    // Update metrics
    botState.balance = newBalance;
    updatePerformanceMetrics();
    loadActivePositions();
    loadRecentTrades();
}

function updateChartPeriod(period) {
    // Update chart based on selected period
    console.log('Updating chart for period:', period);
}

// === CSS ANIMATIONS ===
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
    
    .btn-danger {
        background: var(--gradient-danger);
    }
`;
document.head.appendChild(style);

// Initialize positions and trades
loadActivePositions();
loadRecentTrades();

console.log('🤖 Trading Bot Dashboard Initialized');
