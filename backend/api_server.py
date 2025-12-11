"""
Production API Server
REST API + WebSocket for real-time trading bot platform
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import os
import logging
from datetime import timedelta

# Import services
from services.auth_service import AuthService
from services.payment_service import PaymentService
from database.db_manager import DatabaseManager

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-this')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Initialize extensions
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
jwt = JWTManager(app)

# Initialize services
db_manager = DatabaseManager({'database': {'type': 'sqlite', 'sqlite_path': 'data/production.db'}})
auth_service = AuthService(db_manager)
payment_service = PaymentService(os.getenv('STRIPE_SECRET_KEY'), db_manager)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== AUTH ENDPOINTS ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    data = request.json
    result = auth_service.register_user(
        username=data.get('username'),
        email=data.get('email'),
        password=data.get('password'),
        full_name=data.get('full_name')
    )
    return jsonify(result), 201 if result['success'] else 400


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.json
    result = auth_service.login_user(
        username=data.get('username'),
        password=data.get('password'),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    return jsonify(result), 200 if result['success'] else 401


@app.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    user_id = get_jwt_identity()
    result = auth_service.refresh_token(user_id)
    return jsonify(result)


@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    result = auth_service.logout_user(token)
    return jsonify(result)


@app.route('/api/auth/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    user_id = get_jwt_identity()
    data = request.json
    result = auth_service.change_password(
        user_id=user_id,
        old_password=data.get('old_password'),
        new_password=data.get('new_password')
    )
    return jsonify(result)


# ==================== USER ENDPOINTS ====================

@app.route('/api/user/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    user_id = get_jwt_identity()
    user = db_manager.get_user_by_id(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict())


@app.route('/api/user/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    user_id = get_jwt_identity()
    data = request.json
    
    user = db_manager.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Update allowed fields
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'phone' in data:
        user.phone = data['phone']
  if 'country' in data:
        user.country = data['country']
    
    db_manager.update_user(user)
    
    return jsonify({'success': True, 'user': user.to_dict()})


@app.route('/api/user/trading-settings', methods=['GET'])
@jwt_required()
def get_trading_settings():
    """Get user trading settings"""
    user_id = get_jwt_identity()
    user = db_manager.get_user_by_id(user_id)
    
    return jsonify({
        'auto_trading_enabled': user.auto_trading_enabled,
        'max_position_size': user.max_position_size,
        'max_positions': user.max_positions,
        'daily_loss_limit': user.daily_loss_limit,
        'paper_balance': user.paper_balance
    })


@app.route('/api/user/trading-settings', methods=['PUT'])
@jwt_required()
def update_trading_settings():
    """Update trading settings"""
    user_id = get_jwt_identity()
    data = request.json
    
    user = db_manager.get_user_by_id(user_id)
    
    if 'auto_trading_enabled' in data:
        user.auto_trading_enabled = data['auto_trading_enabled']
    if 'max_position_size' in data:
        user.max_position_size = float(data['max_position_size'])
    if 'max_positions' in data:
        user.max_positions = int(data['max_positions'])
    if 'daily_loss_limit' in data:
        user.daily_loss_limit = float(data['daily_loss_limit'])
    
    db_manager.update_user(user)
    
    return jsonify({'success': True})


# ==================== PAYMENT ENDPOINTS ====================

@app.route('/api/payment/create-customer', methods=['POST'])
@jwt_required()
def create_customer():
    """Create Stripe customer"""
    user_id = get_jwt_identity()
    data = request.json
    
    user = db_manager.get_user_by_id(user_id)
    result = payment_service.create_customer(
        user_id=user_id,
        email=user.email,
        payment_method_id=data.get('payment_method_id')
    )
    
    return jsonify(result)


@app.route('/api/payment/subscribe', methods=['POST'])
@jwt_required()
def subscribe():
    """Create subscription"""
    user_id = get_jwt_identity()
    data = request.json
    
    result = payment_service.create_subscription(
        user_id=user_id,
        plan_type=data.get('plan_type'),  # 'pro' or 'enterprise'
        billing_cycle=data.get('billing_cycle', 'monthly')
    )
    
    return jsonify(result)


@app.route('/api/payment/cancel-subscription', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """Cancel subscription"""
    user_id = get_jwt_identity()
    result = payment_service.cancel_subscription(user_id)
    return jsonify(result)


@app.route('/api/payment/billing-history', methods=['GET'])
@jwt_required()
def billing_history():
    """Get billing history"""
    user_id = get_jwt_identity()
    result = payment_service.get_billing_history(user_id)
    return jsonify(result)


@app.route('/api/payment/webhook', methods=['POST'])
def payment_webhook():
    """Stripe webhook handler"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    result = payment_service.handle_webhook(payload, sig_header, webhook_secret)
    return jsonify(result)


# ==================== TRADING ENDPOINTS ====================

@app.route('/api/trading/start', methods=['POST'])
@jwt_required()
def start_trading():
    """Start auto trading for user"""
    user_id = get_jwt_identity()
    user = db_manager.get_user_by_id(user_id)
    
    limits = user.get_subscription_limits()
    if not limits['real_trading']:
        return jsonify({'error': 'Upgrade to Pro to enable auto trading'}), 403
    
    user.auto_trading_enabled = True
    db_manager.update_user(user)
    
    # Notify via WebSocket
    socketio.emit('trading_started', {'user_id': user_id}, room=f'user_{user_id}')
    
    return jsonify({'success': True, 'message': 'Auto trading started'})


@app.route('/api/trading/stop', methods=['POST'])
@jwt_required()
def stop_trading():
    """Stop auto trading"""
    user_id = get_jwt_identity()
    user = db_manager.get_user_by_id(user_id)
    
    user.auto_trading_enabled = False
    db_manager.update_user(user)
    
    socketio.emit('trading_stopped', {'user_id': user_id}, room=f'user_{user_id}')
    
    return jsonify({'success': True, 'message': 'Auto trading stopped'})


@app.route('/api/trading/positions', methods=['GET'])
@jwt_required()
def get_positions():
    """Get user's trading positions"""
    user_id = get_jwt_identity()
    positions = db_manager.get_user_positions(user_id)
    
    return jsonify({'positions': [p.to_dict() for p in positions]})


@app.route('/api/trading/history', methods=['GET'])
@jwt_required()
def get_trade_history():
    """Get trade history"""
    user_id = get_jwt_identity()
    limit = request.args.get('limit', 100, type=int)
    
    trades = db_manager.get_user_trade_history(user_id, limit=limit)
    
    return jsonify({'trades': [t.to_dict() for t in trades]})


@app.route('/api/trading/performance', methods=['GET'])
@jwt_required()
def get_performance():
    """Get trading performance metrics"""
    user_id = get_jwt_identity()
    stats = db_manager.get_user_performance_stats(user_id)
    
    return jsonify(stats)


# ==================== ADMIN ENDPOINTS ====================

@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def admin_get_users():
    """Get all users (admin only)"""
    user_id = get_jwt_identity()
    user = db_manager.get_user_by_id(user_id)
    
    if not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    users = db_manager.get_all_users()
    return jsonify({'users': [u.to_dict() for u in users]})


@app.route('/api/admin/stats', methods=['GET'])
@jwt_required()
def admin_stats():
    """Get platform statistics (admin only)"""
    user_id = get_jwt_identity()
    user = db_manager.get_user_by_id(user_id)
    
    if not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    stats = {
        'total_users': db_manager.get_total_users(),
        'active_traders': db_manager.get_active_traders_count(),
        'total_trades_today': db_manager.get_trades_count_today(),
        'total_revenue': db_manager.get_total_revenue(),
        'subscription_breakdown': db_manager.get_subscription_breakdown()
    }
    
    return jsonify(stats)


# ==================== WEBSOCKET EVENTS ====================

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to trading bot server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('join_user_room')
def handle_join_user_room(data):
    """Join user-specific room for real-time updates"""
    user_id = data.get('user_id')
    room = f'user_{user_id}'
    join_room(room)
    emit('joined_room', {'room': room})


@socketio.on('leave_user_room')
def handle_leave_user_room(data):
    """Leave user room"""
    user_id = data.get('user_id')
    room = f'user_{user_id}'
    leave_room(room)


# Helper function to emit trade updates
def emit_trade_update(user_id, trade_data):
    """Emit trade update to user's room"""
    socketio.emit('trade_update', trade_data, room=f'user_{user_id}')


def emit_position_update(user_id, position_data):
    """Emit position update"""
    socketio.emit('position_update', position_data, room=f'user_{user_id}')


# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'mode': 'production'
    })


@app.route('/')
def index():
    """API root"""
    return jsonify({
        'name': 'Trading Bot API',
        'version': '2.0.0',
        'docs': '/api/docs'
    })


# ==================== RUN SERVER ====================

if __name__ == '__main__':
    logger.info("Starting Production Trading Bot API Server...")
    logger.info("Server: http://localhost:5000")
    logger.info("WebSocket: ws://localhost:5000")
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=False  # Set to False in production
    )
