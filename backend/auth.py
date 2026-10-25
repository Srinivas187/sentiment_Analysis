"""
Authentication Module
Handles user registration and login
"""

import os
import sys
from pathlib import Path
import bcrypt
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.db_utils import get_user_by_email, create_user, get_user_by_id
from backend.config import JWT_SECRET_KEY, JWT_ACCESS_TOKEN_EXPIRES

logger = logging.getLogger(__name__)


def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password, password_hash):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def generate_token(user_id, email, role='user'):
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.utcnow() + timedelta(seconds=JWT_ACCESS_TOKEN_EXPIRES),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')


def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """Decorator for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except:
                pass
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Verify token
        payload = verify_token(token)
        if payload is None:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        # Add user info to request
        request.current_user = {
            'user_id': payload['user_id'],
            'email': payload['email'],
            'role': payload['role']
        }
        
        return f(*args, **kwargs)
    
    return decorated


def register_user_handler(name, email, password):
    """Register new user"""
    try:
        # Check if user exists
        existing_user = get_user_by_email(email)
        if existing_user:
            return {'success': False, 'error': 'User with this email already exists'}
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user
        if create_user(name, email, password_hash):
            return {'success': True, 'message': 'User registered successfully'}
        else:
            return {'success': False, 'error': 'Failed to create user'}
    
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        return {'success': False, 'error': str(e)}


def login_user_handler(email, password):
    """Login user"""
    try:
        # Get user
        user = get_user_by_email(email)
        if not user:
            return {'success': False, 'error': 'Invalid email or password'}
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            return {'success': False, 'error': 'Invalid email or password'}
        
        # Generate token
        token = generate_token(user['user_id'], user['email'], user.get('role', 'user'))
        
        return {
            'success': True,
            'token': token,
            'user': {
                'user_id': user['user_id'],
                'name': user['name'],
                'email': user['email'],
                'role': user.get('role', 'user')
            }
        }
    
    except Exception as e:
        logger.error(f"Error logging in user: {e}")
        return {'success': False, 'error': str(e)}
