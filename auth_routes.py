from flask import Blueprint, jsonify, session, redirect, url_for, request
from oauthlib.oauth2 import WebApplicationClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests
import json
from functools import wraps

auth_bp = Blueprint('auth', __name__)
client = WebApplicationClient(os.environ.get('GOOGLE_CLIENT_ID'))

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# In-memory user store (replace with database in production)
users = {
    'admin@admin.com': {
        'id': 'admin',
        'email': 'admin@admin.com',
        'username': 'admin',
        'password': generate_password_hash('admin'),
        'age': 30,
        'role': 'admin'
    }
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            return jsonify({'message': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get('user')
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')
    age = data.get('age')

    if not all([email, password, username, age]):
        return jsonify({'message': 'Missing required fields'}), 400

    if email in users:
        return jsonify({'message': 'Email already registered'}), 400

    user = {
        'id': email,  # Using email as ID for simplicity
        'email': email,
        'username': username,
        'password': generate_password_hash(password),
        'age': age,
        'role': 'user'
    }

    users[email] = user
    session_user = {k: v for k, v in user.items() if k != 'password'}
    session['user'] = session_user

    return jsonify({
        'message': 'Registration successful',
        'user': session_user
    })

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing email or password'}), 400

    user = users.get(email)
    if user and check_password_hash(user['password'], password):
        session_user = {k: v for k, v in user.items() if k != 'password'}
        session['user'] = session_user
        return jsonify({
            'message': 'Login successful',
            'user': session_user
        })

    return jsonify({'message': 'Invalid email or password'}), 401

@auth_bp.route('/api/auth/google')
def google_login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    
    # Utiliser l'URL complète de Replit
    redirect_uri = "https://solo-rpg-ai-narrator.replit.app/api/auth/google/callback"
    
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=redirect_uri,
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@auth_bp.route('/api/auth/google/callback')
def callback():
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Utiliser l'URL complète de Replit pour le callback
    redirect_url = "https://solo-rpg-ai-narrator.replit.app/api/auth/google/callback"
    
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.base_url.replace('http://localhost:5000', 'https://solo-rpg-ai-narrator.replit.app') + '?' + request.query_string.decode(),
        redirect_url=redirect_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(os.environ.get('GOOGLE_CLIENT_ID'), os.environ.get('GOOGLE_CLIENT_SECRET')),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        user_email = userinfo_response.json()["email"]
        username = userinfo_response.json()["given_name"]
        picture = userinfo_response.json()["picture"]

        # Create or update user
        if user_email not in users:
            users[user_email] = {
                'id': unique_id,
                'email': user_email,
                'username': username,
                'picture': picture,
                'role': 'user'
            }

        session_user = users[user_email]
        session['user'] = session_user
        return redirect('https://solo-rpg-ai-narrator.replit.app/')
    return "User email not available or not verified", 400

@auth_bp.route('/api/auth/status')
def auth_status():
    user = session.get('user')
    return jsonify({'user': user})

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'message': 'Logged out successfully'})

# Protected route example
@auth_bp.route('/api/auth/protected')
@login_required
def protected():
    return jsonify({'message': 'This is a protected route'})

# Admin route example
@auth_bp.route('/api/auth/admin')
@admin_required
def admin():
    return jsonify({'message': 'This is an admin route'})
