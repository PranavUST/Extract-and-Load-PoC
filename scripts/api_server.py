import sys
import logging
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from run_pipeline import run_ingestion
from src.logging_utils import setup_logging
import threading
import os
from passlib.context import CryptContext
import psycopg2
from psycopg2 import sql
from src.database import get_connection  # Import your connection function
import logging     # Import logger instan   ce
from src.database import create_logins_table_if_not_exists
from functools import wraps

create_logins_table_if_not_exists()

# Configure logging with absolute path
log_file_path = str(Path(__file__).parent.parent / "pipeline.log")
setup_logging(log_file=log_file_path)

execution_cycle = 0  # Added execution counter
print("Current working directory:", os.getcwd())
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Or 'None' if using HTTPS
app.config['SESSION_COOKIE_SECURE'] = False    # True in production

# Proper CORS configuration for credentials
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": ["http://localhost:4200"],  # Explicit origin, not wildcard
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    }
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _build_cors_preflight_response():
    response = jsonify({"status": "preflight"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'OK'})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:4200")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
        response.headers.add('Access-Control-Allow-Methods', "GET,POST,PUT,DELETE,OPTIONS")
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, password, role, name, email FROM logins 
            WHERE username = %s
        """, (username,))
        user = cur.fetchone()
        
        if user and pwd_context.verify(password, user[1]):
            # Create session
            session['user_id'] = user[0]
            session['role'] = user[2]
            session['username'] = username
            
            # Update last login
            cur.execute("""
                UPDATE logins 
                SET last_login = NOW() 
                WHERE id = %s
            """, (user[0],))
            conn.commit()
            
            return jsonify({
                "success": True,
                "role": user[2],
                "username": username,
                "name": user[3] or "",
                "email": user[4] or ""
            })
            
        return jsonify({"success": False, "error": "Invalid credentials"}), 401
        
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        return jsonify({"success": False, "error": "Login failed"}), 500

@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    data = request.get_json()
    hashed_pwd = pwd_context.hash(data['password'])
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO logins 
                (name, email, role, username, password)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data.get('name'),
            data.get('email'),
            data.get('role', 'User'),
            data['username'],
            hashed_pwd
        ))
        conn.commit()
        return jsonify({"success": True})
        
    except psycopg2.errors.UniqueViolation:
        return jsonify({
            "success": False,
            "error": "Username or email already exists"
        }), 400
    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        return jsonify({"success": False}), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

@app.route('/api/logout', methods=['POST', 'OPTIONS'])
def logout():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    session.pop('user_id', None)
    session.pop('role', None)
    return jsonify({"success": True})


def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'Admin':
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Store status in memory for demo purposes
pipeline_status = {"status": "idle", "message": ""}
status_lock = threading.Lock()

@app.route('/api/users', methods=['GET', 'OPTIONS'])
@require_admin
def get_users():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, email, username, role, last_login 
            FROM logins 
            ORDER BY name
        """)
        users = cur.fetchall()
        
        user_list = []
        for user in users:
            user_list.append({
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'username': user[3],
                'role': user[4],
                'last_login': user[5].isoformat() if user[5] else None
            })
        
        return jsonify({'success': True, 'users': user_list})
        
    except Exception as e:
        logging.error(f"Get users error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

@app.route('/api/users/<int:user_id>/role', methods=['PUT', 'OPTIONS'])
@require_admin
def update_user_role(user_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    data = request.get_json()
    new_role = data.get('role')
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE logins 
            SET role = %s 
            WHERE id = %s
        """, (new_role, user_id))
        conn.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        logging.error(f"Update user role error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

@app.route('/api/users/<int:user_id>', methods=['DELETE', 'OPTIONS'])
@require_admin
def delete_user(user_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM logins WHERE id = %s", (user_id,))
        conn.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        logging.error(f"Delete user error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

def run_pipeline_thread(config_file):
    global execution_cycle
    execution_cycle += 1
    logging.info(f"--- Pipeline Execution Cycle: {execution_cycle} ---")
    
    try:
        if not os.path.isabs(config_file):
            config_file = str(Path(__file__).parent.parent / config_file)
        
        with status_lock:
            pipeline_status["status"] = "running"
            pipeline_status["message"] = "Pipeline is running"
        
        run_ingestion(config_file)
        
        with status_lock:
            pipeline_status["status"] = "success"
            pipeline_status["message"] = "Pipeline completed successfully"
    except Exception as e:
        with status_lock:  # Maintain thread safety for error status
            pipeline_status["status"] = "error"
            pipeline_status["message"] = str(e)
    finally:
        logging.info("-" * 80)  # Add separator after each execution

@app.route('/run-pipeline', methods=['POST', 'OPTIONS'])
def run_pipeline_api():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    data = request.get_json()
    config_file = data.get("config_file")
    if not config_file:
        return jsonify({"status": "error", "message": "No config file provided"}), 400
    
    threading.Thread(target=run_pipeline_thread, args=(config_file,), daemon=True).start()
    return jsonify({"status": "started"})

@app.route('/pipeline-status', methods=['GET'])
def get_status():
    with status_lock:
        return jsonify(pipeline_status)

@app.route('/v1/data', methods=['GET'])
def get_data():
    return jsonify([])

if __name__ == "__main__":
    app.run(port=5000)
