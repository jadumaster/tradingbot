"""
Authentication Service
Handles user registration, login, JWT tokens
"""

from flask import jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from datetime import timedelta
import logging
from models.user import User, UserSession
from database.db_manager import DatabaseManager


class AuthService:
    """Authentication and authorization service"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
    
    def register_user(self, username, email, password, full_name=None):
        """Register a new user"""
        try:
            # Check if user exists
            if self.db.get_user_by_username(username):
                return {'success': False, 'message': 'Username already exists'}
            
            if self.db.get_user_by_email(email):
                return {'success': False, 'message': 'Email already exists'}
            
            # Create user
            user = User(
                username=username,
                email=email,
                password=password,
                full_name=full_name
            )
            
            self.db.create_user(user)
            
            # Send verification email (TODO: implement)
            
            self.logger.info(f"New user registered: {username}")
            
            return {
                'success': True,
                'message': 'Registration successful',
                'user': user.to_dict()
            }
            
        except Exception as e:
            self.logger.error(f"Registration error: {e}")
            return {'success': False, 'message': 'Registration failed'}
    
    def login_user(self, username, password, ip_address=None, user_agent=None):
        """Login user and create session"""
        try:
            # Get user
            user = self.db.get_user_by_username(username)
            
            if not user:
                return {'success': False, 'message': 'Invalid credentials'}
            
            # Check password
            if not user.check_password(password):
                return {'success': False, 'message': 'Invalid credentials'}
            
            # Check if account is active
            if not user.is_active:
                return {'success': False, 'message': '

 is disabled'}
            
            # Create JWT tokens
            access_token = create_access_token(
                identity=user.id,
                expires_delta=timedelta(hours=24)
            )
            refresh_token = create_refresh_token(
                identity=user.id,
                expires_delta=timedelta(days=30)
            )
            
            # Create session
            session = UserSession(
                user_id=user.id,
                token=access_token,
                ip_address=ip_address,
                user_agent=user_agent
            )
            self.db.create_session(session)
            
            # Update last login
            self.db.update_user_last_login(user.id)
            
            self.logger.info(f"User logged in: {username}")
            
            return {
                'success': True,
                'message': 'Login successful',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }
            
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return {'success': False, 'message': 'Login failed'}
    
    def refresh_token(self, user_id):
        """Refresh access token"""
        try:
            access_token = create_access_token(
                identity=user_id,
                expires_delta=timedelta(hours=24)
            )
            
            return {
                'success': True,
                'access_token': access_token
            }
            
        except Exception as e:
            self.logger.error(f"Token refresh error: {e}")
            return {'success': False, 'message': 'Token refresh failed'}
    
    def logout_user(self, token):
        """Logout user and invalidate session"""
        try:
            session = self.db.get_session_by_token(token)
            if session:
                self.db.invalidate_session(session.id)
            
            return {'success': True, 'message': 'Logged out successfully'}
            
        except Exception as e:
            self.logger.error(f"Logout error: {e}")
            return {'success': False, 'message': 'Logout failed'}
    
    def verify_session(self, token):
        """Verify if session is valid"""
        try:
            session = self.db.get_session_by_token(token)
            
            if not session:
                return False
            
            if not session.is_active:
                return False
            
            if session.is_expired():
                self.db.invalidate_session(session.id)
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Session verification error: {e}")
            return False
    
    def change_password(self, user_id, old_password, new_password):
        """Change user password"""
        try:
            user = self.db.get_user_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            if not user.check_password(old_password):
                return {'success': False, 'message': 'Invalid current password'}
            
            user.set_password(new_password)
            self.db.update_user(user)
            
            # Invalidate all sessions
            self.db.invalidate_all_user_sessions(user_id)
            
            self.logger.info(f"Password changed for user: {user.username}")
            
            return {'success': True, 'message': 'Password changed successfully'}
            
        except Exception as e:
            self.logger.error(f"Password change error: {e}")
            return {'success': False, 'message': 'Password change failed'}
    
    def request_password_reset(self, email):
        """Request password reset"""
        try:
            user = self.db.get_user_by_email(email)
            
            if not user:
                # Don't reveal if email exists
                return {'success': True, 'message': 'If email exists, reset link sent'}
            
            # Create reset token (TODO: implement)
            # Send reset email (TODO: implement)
            
            self.logger.info(f"Password reset requested for: {email}")
            
            return {'success': True, 'message': 'Password reset link sent to email'}
            
        except Exception as e:
            self.logger.error(f"Password reset error: {e}")
            return {'success': False, 'message': 'Password reset failed'}
