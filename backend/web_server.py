"""
Web Server for Trading Bot Dashboard
Serves the frontend and provides API endpoints
"""

from flask import Flask, render_template, jsonify, send_from_directory
from flask_cors import CORS
import os
import webbrowser
import threading
from pathlib import Path

app = Flask(__name__, 
            static_folder='../frontend',
            template_folder='../frontend')
CORS(app)


@app.route('/')
def index():
    """Serve the main dashboard"""
    return send_from_directory('../frontend', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('../frontend', path)


@app.route('/api/status')
def get_status():
    """Get bot status"""
    return jsonify({
        'running': True,
        'mode': 'paper',
        'balance': 10000,
        'open_positions': 2
    })


@app.route('/api/performance')
def get_performance():
    """Get performance metrics"""
    return jsonify({
        'total_pnl': 450.25,
        'win_rate': 65.5,
        'total_trades': 42,
        'sharpe_ratio': 1.85
    })


@app.route('/api/positions')
def get_positions():
    """Get open positions"""
    return jsonify({
        'positions': []
    })


@app.route('/api/trades')
def get_trades():
    """Get trade history"""
    return jsonify({
        'trades': []
    })


def start_dashboard(config, port=8080):
    """
    Start the web dashboard
    
    Args:
        config: Bot configuration
        port: Port to run on
    """
    host = config['dashboard']['host']
    auto_open = config['dashboard'].get('auto_open', True)
    
    print(f"\n🌐 Starting Web Dashboard...")
    print(f"📍 URL: http://{host}:{port}")
    print(f"Press Ctrl+C to stop\n")
    
    # Open browser automatically
    if auto_open:
        threading.Timer(1.5, lambda: webbrowser.open(f'http://{host}:{port}')).start()
    
    # Run Flask app
    app.run(host=host, port=port, debug=False)


if __name__ == '__main__':
    # For standalone testing
    from utils.helpers import load_config
    
    config_path = Path(__file__).parent.parent / 'config.yaml'
    config = load_config(config_path)
    
    start_dashboard(config)
