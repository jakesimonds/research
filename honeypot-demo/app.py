#!/usr/bin/env python3
"""
Educational Honeypot - Fake Vulnerable Web App
Logs all requests to see bot activity in the wild
"""
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
import geoip2.database
import os

app = Flask(__name__)

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler('/var/log/honeypot/access.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Stats counter
stats = {
    'total_requests': 0,
    'unique_ips': set(),
    'common_paths': {},
    'sql_injection_attempts': 0,
    'credential_attempts': 0
}

def log_request():
    """Log detailed request information"""
    stats['total_requests'] += 1
    stats['unique_ips'].add(request.remote_addr)

    path = request.path
    stats['common_paths'][path] = stats['common_paths'].get(path, 0) + 1

    # Detect SQL injection attempts
    query_string = request.query_string.decode('utf-8', errors='ignore')
    full_path = f"{path}?{query_string}" if query_string else path
    if any(keyword in full_path.lower() for keyword in ['union', 'select', '1=1', 'drop', 'insert', '--', 'or 1']):
        stats['sql_injection_attempts'] += 1

    # Get POST data if available
    post_data = None
    if request.method == 'POST':
        try:
            if request.is_json:
                post_data = request.get_json()
            else:
                post_data = request.form.to_dict()

            # Count credential attempts
            if any(key in str(post_data).lower() for key in ['password', 'passwd', 'pwd', 'pass']):
                stats['credential_attempts'] += 1
        except:
            post_data = request.get_data(as_text=True)[:500]  # Limit size

    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'ip': request.remote_addr,
        'method': request.method,
        'path': path,
        'query_string': query_string,
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'referer': request.headers.get('Referer', 'None'),
        'content_type': request.headers.get('Content-Type', 'None'),
        'post_data': post_data,
        'headers': dict(request.headers)
    }

    logger.info(json.dumps(log_entry))
    return log_entry

# Fake homepage - looks like a real (vulnerable) app
HOME_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>SecureStore Admin Portal</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        .login-box { border: 1px solid #ccc; padding: 20px; background: #f9f9f9; }
        input { margin: 5px 0; padding: 8px; width: 100%; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
        .version { color: #888; font-size: 12px; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>🔐 SecureStore Admin Portal</h1>
    <div class="login-box">
        <h2>Administrator Login</h2>
        <form action="/admin/login" method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
    <div class="version">
        Powered by WordPress 5.4.2 | PHP 7.2 | MySQL 5.7<br>
        <a href="/admin">Admin Dashboard</a> |
        <a href="/phpmyadmin">Database</a> |
        <a href="/api/docs">API Docs</a>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    log_request()
    return HOME_PAGE

# Common WordPress targets
@app.route('/wp-admin')
@app.route('/wp-admin/')
@app.route('/wp-login.php')
def wordpress_admin():
    log_request()
    return """
    <html><head><title>WordPress Admin</title></head>
    <body>
        <h1>WordPress Login</h1>
        <form method="POST" action="/wp-login.php">
            <input name="log" placeholder="Username"><br>
            <input type="password" name="pwd" placeholder="Password"><br>
            <button>Log In</button>
        </form>
        <p style="color: red;"><!-- Debug: MySQL connection failed - root@localhost:3306 --></p>
    </body></html>
    """, 200

@app.route('/wp-login.php', methods=['POST'])
def wordpress_login():
    log_request()
    return "ERROR: Invalid username or password. Please try again.", 401

@app.route('/xmlrpc.php', methods=['GET', 'POST'])
def xmlrpc():
    log_request()
    return """<?xml version="1.0" encoding="UTF-8"?>
    <methodResponse>
        <fault>
            <value><string>Method not found</string></value>
        </fault>
    </methodResponse>""", 200

# PHPMyAdmin targets
@app.route('/phpmyadmin')
@app.route('/phpmyadmin/')
@app.route('/pma')
@app.route('/mysql')
def phpmyadmin():
    log_request()
    return """
    <html><head><title>phpMyAdmin 4.8.5</title></head>
    <body>
        <h1>phpMyAdmin 4.8.5</h1>
        <form method="POST" action="/phpmyadmin/index.php">
            <input name="pma_username" placeholder="Username"><br>
            <input type="password" name="pma_password" placeholder="Password"><br>
            <button>Go</button>
        </form>
        <p>Server: localhost:3306</p>
    </body></html>
    """, 200

# Common config/env file targets
@app.route('/.env')
@app.route('/config.php')
@app.route('/.git/config')
@app.route('/config.json')
def config_files():
    log_request()
    # Return fake but realistic-looking config to keep them engaged
    return """
# Database Configuration
DB_HOST=localhost
DB_USER=admin
DB_PASS=change_me_123
DB_NAME=production_db

# API Keys (DO NOT COMMIT)
API_KEY=sk_test_fake_key_12345
AWS_ACCESS_KEY=AKIA_FAKE_KEY
SECRET_KEY=super_secret_key_change_this
    """, 200

# Admin panels
@app.route('/admin')
@app.route('/admin/')
@app.route('/administrator')
@app.route('/admin/login')
def admin():
    log_request()
    return """
    <html><head><title>Admin Dashboard</title></head>
    <body>
        <h1>Admin Dashboard</h1>
        <p>You must be logged in to view this page.</p>
        <form method="POST" action="/admin/login">
            <input name="username" placeholder="Username"><br>
            <input type="password" name="password" placeholder="Password"><br>
            <button>Login</button>
        </form>
    </body></html>
    """, 200

@app.route('/admin/login', methods=['POST'])
def admin_login():
    log_request()
    return jsonify({
        "error": "Invalid credentials",
        "message": "Authentication failed for user",
        "code": 401
    }), 401

# API endpoints
@app.route('/api/docs')
@app.route('/api/v1/users')
@app.route('/api/config')
def api_endpoints():
    log_request()
    return jsonify({
        "version": "1.0",
        "endpoints": [
            "/api/v1/users",
            "/api/v1/auth",
            "/api/v1/admin",
            "/api/config"
        ],
        "authentication": "Bearer token required"
    }), 200

@app.route('/api/v1/auth', methods=['POST'])
def api_auth():
    log_request()
    return jsonify({
        "error": "Invalid API key",
        "message": "Authentication failed"
    }), 401

# Shell/Command injection targets
@app.route('/shell')
@app.route('/cmd')
@app.route('/console')
def shell():
    log_request()
    cmd = request.args.get('cmd', '')
    return f"""
    <html><head><title>Debug Console</title></head>
    <body>
        <h1>Debug Console</h1>
        <form>
            <input name="cmd" placeholder="Enter command" value="{cmd}"><br>
            <button>Execute</button>
        </form>
        <pre>Error: exec() has been disabled for security reasons</pre>
    </body></html>
    """, 200

# Catch-all for any other path
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def catch_all(path):
    log_request()
    return jsonify({
        "error": "Not found",
        "path": f"/{path}",
        "message": "The requested resource was not found on this server"
    }), 404

# Stats endpoint (not advertised to bots)
@app.route('/honeypot/stats')
def show_stats():
    log_request()
    return jsonify({
        "total_requests": stats['total_requests'],
        "unique_ips": len(stats['unique_ips']),
        "top_paths": sorted(stats['common_paths'].items(), key=lambda x: x[1], reverse=True)[:20],
        "sql_injection_attempts": stats['sql_injection_attempts'],
        "credential_attempts": stats['credential_attempts']
    }), 200

if __name__ == '__main__':
    # Create log directory
    os.makedirs('/var/log/honeypot', exist_ok=True)

    # Run on port 80, accessible from anywhere
    app.run(host='0.0.0.0', port=80, debug=False)
