import sys
import yaml
import json
import logging
import uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from run_pipeline import run_ingestion
from src.logging_utils import setup_logging
import threading
import os
import signal
import subprocess
import threading
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PIPELINE_PID_FILE = os.path.join(BASE_DIR, '../pipeline.pid')
from passlib.context import CryptContext
import psycopg2
from psycopg2 import sql
from src.database import get_connection  # Import your connection function
import logging     # Import logger instan   ce
from src.database import create_logins_table_if_not_exists
from src.database import create_pipeline_status_table_if_not_exists
create_pipeline_status_table_if_not_exists()
from functools import wraps
from run_pipeline import run_ingestion, main as run_pipeline_main

create_logins_table_if_not_exists()
# Set up logger
logger = logging.getLogger(__name__)

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
# Updated CORS Configuration
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": ["http://localhost:4200"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        },
        r"/saved-*": {  # Covers /saved-source-configs and /saved-target-configs
            "origins": ["http://localhost:4200"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type"],
            "supports_credentials": True
        },
        r"/run-pipeline": {
            "origins": ["http://localhost:4200"],
            "methods": ["POST", "OPTIONS"],
            "allow_headers": ["Content-Type"],
            "supports_credentials": True
        },
        r"/run-pipeline-once": {
            "origins": ["http://localhost:4200"],
            "methods": ["POST", "OPTIONS"],
            "allow_headers": ["Content-Type"],
            "supports_credentials": True
        },
        r"/pipeline-status": {
            "origins": ["http://localhost:4200"],
            "methods": ["GET", "OPTIONS"],
            "allow_headers": ["Content-Type"],
            "supports_credentials": True
        },
        r"/stop-pipeline": {
            "origins": ["http://localhost:4200"],
            "methods": ["POST", "OPTIONS"],
            "allow_headers": ["Content-Type"],
            "supports_credentials": True
        },
        r"/current-config": {
            "origins": ["http://localhost:4200"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"],
            "supports_credentials": True
        },
        r"/source-configs": {
            "origins": ["http://localhost:4200"],
            "methods": ["POST", "OPTIONS"],
            "allow_headers": ["Content-Type"],
            "supports_credentials": True
        },
        r"/target-configs": {
            "origins": ["http://localhost:4200"],
            "methods": ["POST", "OPTIONS"],
            "allow_headers": ["Content-Type"],
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

@app.route('/api/users/<int:user_id>', methods=['PUT', 'OPTIONS'])
def update_user(user_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    data = request.get_json()
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE logins
            SET name = %s, email = %s, username = %s
            WHERE id = %s
        """, (data.get('name'), data.get('email'), data.get('username'), user_id))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Update user error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

@app.route('/api/users/<int:user_id>/password', methods=['PUT'])
def change_password(user_id):
    user_id_session = session.get('user_id')
    if not user_id_session or user_id_session != user_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    data = request.get_json()
    new_password = data.get('password')
    if not new_password or len(new_password) < 6:
        return jsonify({'success': False, 'error': 'Password must be at least 6 characters.'}), 400
    try:
        conn = get_connection()
        cur = conn.cursor()
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_pwd = pwd_context.hash(new_password)
        cur.execute("UPDATE logins SET password = %s WHERE id = %s", (hashed_pwd, user_id))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

def run_pipeline_thread(config_file, run_id=None):
    global execution_cycle
    execution_cycle += 1
    logging.info(f"--- Pipeline Execution Cycle: {execution_cycle} ---")
    try:
        if not os.path.isabs(config_file):
            config_file = str(Path(__file__).parent.parent / config_file)
        with status_lock:
            pipeline_status["status"] = "running"
            pipeline_status["message"] = "Pipeline is running"
        run_ingestion(config_file, run_id=run_id)  # Pass run_id to ingestion
        with status_lock:
            pipeline_status["status"] = "success"
            pipeline_status["message"] = "Pipeline completed successfully"
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}")
        with status_lock:
            pipeline_status["status"] = "error"
            pipeline_status["message"] = str(e)
    finally:
        logging.info("-" * 80)

@app.route('/run-pipeline', methods=['POST', 'OPTIONS'])
def run_pipeline_api():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON data provided"}), 400
            
        config_file = data.get("config_file")
        interval = data.get("interval")
        duration = data.get("duration")
        if not config_file:
            return jsonify({"status": "error", "message": "No config file provided"}), 400
        if not interval or not duration:
            return jsonify({"status": "error", "message": "Interval and duration required"}), 400

        # Start the scheduler in a thread
        import subprocess
        import sys
        def run_scheduler():
            script_path = os.path.join(os.path.dirname(__file__), "run_pipeline.py")
            project_root = os.path.dirname(os.path.dirname(__file__))
            proc = subprocess.Popen([
                sys.executable, script_path,
                config_file,
                "--interval", str(interval),
                "--duration", str(duration)
            ], cwd=project_root)
            # Save the PID
            with open(PIPELINE_PID_FILE, 'w') as f:
                f.write(str(proc.pid))
        threading.Thread(target=run_scheduler, daemon=True).start()
        return jsonify({"status": "started"})
    except Exception as e:
        logger.error(f"Error starting pipeline: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to start pipeline"}), 500
@app.route('/run-pipeline-once', methods=['POST', 'OPTIONS'])
def run_pipeline_once_api():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    try:
        data = request.get_json()
        config_file = data.get("config_file")
        if not config_file:
            return jsonify({"status": "error", "message": "No config file provided"}), 400

        run_id = str(uuid.uuid4())

        def run_once():
            run_pipeline_thread(config_file, run_id)  # Pass run_id to thread
        threading.Thread(target=run_once, daemon=True).start()
        return jsonify({"status": "started", "run_id": run_id})  # Return run_id to frontend
    except Exception as e:
        logger.error(f"Error running pipeline once: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to run pipeline once"}), 500
    
@app.route('/latest-scheduled-run-id', methods=['GET'])
def get_latest_scheduled_run_id():
    try:
        with open('latest_scheduled_run_id.txt') as f:
            run_id = f.read().strip()
        return jsonify({"run_id": run_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stop-pipeline', methods=['POST'])
def stop_pipeline():
    try:
        if not os.path.exists(PIPELINE_PID_FILE):
            return jsonify({"status": "error", "message": "No running pipeline found"}), 404
        with open(PIPELINE_PID_FILE, 'r') as f:
            pid = int(f.read())
        os.kill(pid, signal.SIGTERM)
        os.remove(PIPELINE_PID_FILE)
        return jsonify({"status": "stopped"})
    except Exception as e:
        logger.error(f"Error stopping pipeline: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to stop pipeline"}), 500
@app.route('/pipeline-status', methods=['GET'])
def get_pipeline_status():
    run_id = request.args.get('run_id')
    conn = get_connection()
    with conn.cursor() as cur:
        if run_id:
            cur.execute("SELECT timestamp, message FROM pipeline_status WHERE run_id = %s ORDER BY id DESC LIMIT 20", (run_id,))
        else:
            cur.execute("SELECT timestamp, message FROM pipeline_status ORDER BY id DESC LIMIT 20")
        rows = cur.fetchall()
    conn.close()
    status = [{"timestamp": str(row[0]), "message": row[1]} for row in rows]
    return jsonify({"status": status})

@app.route('/v1/data', methods=['GET'])
def get_data():
    return jsonify([])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/saved-source-configs', methods=['GET'])
def get_saved_source_configs():
    try:
        path = os.path.join(BASE_DIR, '../config/saved_source_configs.json')
        if not os.path.exists(path):
            return jsonify([])
        with open(path, 'r') as f:
            return jsonify(json.load(f))
    except Exception as e:
        logger.error(f"Error reading saved source configs: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to read configurations"}), 500

@app.route('/saved-source-configs/<name>', methods=['DELETE'])
def delete_saved_source_config(name):
    try:
        path = os.path.join(BASE_DIR, '../config/saved_source_configs.json')
        if not os.path.exists(path):
            return jsonify({"status": "error", "message": "No configs found"}), 404
        with open(path, 'r') as f:
            configs = json.load(f)
        # Compare trimmed names
        configs = [c for c in configs if c.get('name', '').strip() != name.strip()]
        with open(path, 'w') as f:
            json.dump(configs, f)
 
        # --- NEW: Clear current source if deleted ---
        current_path = os.path.join(BASE_DIR, '../config/current_config.json')
        if os.path.exists(current_path):
            with open(current_path, 'r') as f:
                current = json.load(f)
            print(f"Deleting: {name}, Current source: {current.get('source')}")
            if (current.get('source') or '').strip() == name.strip():
                current['source'] = None
                with open(current_path, 'w') as f:
                    json.dump(current, f)
        # --- END NEW ---
 
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Error deleting source config: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to delete configuration"}), 500
        
@app.route('/saved-source-configs/<name>', methods=['PUT'])
def edit_saved_source_config(name):
    try:
        data = request.get_json()
        path = os.path.join(BASE_DIR, '../config/saved_source_configs.json')
        if not os.path.exists(path):
            return jsonify({"status": "error", "message": "No configs found"}), 404
        with open(path, 'r') as f:
            configs = json.load(f)
        updated = False
        for i, c in enumerate(configs):
            if c.get('name') == name:
                configs[i] = data
                updated = True
                break
        if not updated:
            return jsonify({"status": "error", "message": "Config not found"}), 404
        with open(path, 'w') as f:
            json.dump(configs, f)

        source_type = data.get('type', '').upper()
        if source_type == 'API':
            config_path = os.path.join(BASE_DIR, '../config/api_config.yaml')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                if 'source' not in config:
                    config['source'] = {}
                if 'api' not in config['source']:
                    config['source']['api'] = {}
                if 'auth' not in config['source']['api']:
                    config['source']['api']['auth'] = {}
                config['source']['api']['url'] = data.get('endpoint', '')
                config['source']['api']['auth']['token'] = data.get('authToken', '')
                retries = data.get('retries')
                if retries is not None:
                    config['source']['api']['retries'] = int(retries)
                with open(config_path, 'w') as f:
                    yaml.safe_dump(config, f)
        elif source_type == 'FTP':
            config_path = os.path.join(BASE_DIR, '../config/ftp_config.yaml')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    if 'source' not in config:
                        config['source'] = {}
                    if 'ftp' not in config['source']:
                        config['source']['ftp'] = {}
                    config['source']['ftp']['host'] = data.get('ftpHost', '')
                    config['source']['ftp']['username'] = data.get('ftpUsername', '')
                    config['source']['ftp']['password'] = data.get('ftpPassword', '')
                    retries = data.get('retries')
                    if retries is not None:
                        config['source']['ftp']['retries'] = int(retries)
                    with open(config_path, 'w') as f:
                        yaml.safe_dump(config, f)
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Error editing source config: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to edit configuration"}), 500
    
@app.route('/source-configs', methods=['POST'])
def save_source_config():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON data provided"}), 400
            
        source_type = data.get('type')  # 'API' or 'FTP'
        
        if source_type == 'API':
            config_path = os.path.join(BASE_DIR, '../config/api_config.yaml')
            config_path = os.path.abspath(config_path)
            
            if not os.path.exists(config_path):
                return jsonify({"status": "error", "message": "API config file not found"}), 404
                
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                
            # Update API config fields
            if 'source' not in config:
                config['source'] = {}
            if 'api' not in config['source']:
                config['source']['api'] = {}
            if 'auth' not in config['source']['api']:
                config['source']['api']['auth'] = {}
                
            config['source']['api']['url'] = data.get('endpoint', '')
            config['source']['api']['auth']['token'] = data.get('authToken', '')
            retries = data.get('retries')
            if retries is not None:
                config['source']['api']['retries'] = int(retries)

            with open(config_path, 'w') as f:
                yaml.safe_dump(config, f)
                
            # Save to saved configs
            path = os.path.join(BASE_DIR, '../config/saved_source_configs.json')
            configs = []
            if os.path.exists(path):
                with open(path, 'r') as f:
                    configs = json.load(f)
            configs.append(data)
            with open(path, 'w') as f:
                json.dump(configs, f)
                
            return jsonify({"status": "success", "message": "API config updated"}), 200

        elif source_type == 'FTP':
            config_path = os.path.join(BASE_DIR, '../config/ftp_config.yaml')
            config_path = os.path.abspath(config_path)
            
            if not os.path.exists(config_path):
                return jsonify({"status": "error", "message": "FTP config file not found"}), 404
                
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                
            # Update FTP config fields
            if 'source' not in config:
                config['source'] = {}
            if 'ftp' not in config['source']:
                config['source']['ftp'] = {}
                
            config['source']['ftp']['host'] = data.get('ftpHost', '')
            config['source']['ftp']['username'] = data.get('ftpUsername', config['source']['ftp'].get('username', ''))
            config['source']['ftp']['password'] = data.get('ftpPassword', config['source']['ftp'].get('password', ''))
            retries = data.get('retries')
            if retries is not None:
                config['source']['ftp']['retries'] = int(retries)

            with open(config_path, 'w') as f:
                yaml.safe_dump(config, f)
                
            # Save to saved configs
            path = os.path.join(BASE_DIR, '../config/saved_source_configs.json')
            configs = []
            if os.path.exists(path):
                with open(path, 'r') as f:
                    configs = json.load(f)
            configs.append(data)
            with open(path, 'w') as f:
                json.dump(configs, f)
                
            return jsonify({"status": "success", "message": "FTP config updated"}), 200

        else:
            return jsonify({"status": "error", "message": "Unknown source type"}), 400
            
    except Exception as e:
        logger.error(f"Error saving source config: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to save configuration"}), 500

@app.route('/saved-target-configs', methods=['GET'])
def get_saved_target_configs():
    try:
        path = os.path.join(BASE_DIR, '../config/saved_target_configs.json')
        if not os.path.exists(path):
            return jsonify([])
        with open(path, 'r') as f:
            return jsonify(json.load(f))
    except Exception as e:
        logger.error(f"Error reading saved target configs: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to read configurations"}), 500
    
@app.route('/saved-target-configs/<name>', methods=['PUT'])
def edit_saved_target_config(name):
    try:
        data = request.get_json()
        path = os.path.join(BASE_DIR, '../config/saved_target_configs.json')
        if not os.path.exists(path):
            return jsonify({"status": "error", "message": "No configs found"}), 404
        with open(path, 'r') as f:
            configs = json.load(f)
        updated = False
        for i, c in enumerate(configs):
            if c.get('name') == name:
                configs[i] = data
                updated = True
                break
        if not updated:
            return jsonify({"status": "error", "message": "Config not found"}), 404
        with open(path, 'w') as f:
            json.dump(configs, f)

        # --- NEW: Update YAML files ---
        table_name = data.get('tableName')
        if data.get('type') == 'Database' and table_name:
            for yaml_file in ['../config/api_config.yaml', '../config/ftp_config.yaml']:
                config_path = os.path.join(BASE_DIR, yaml_file)
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        config = yaml.safe_load(f)
                    if 'destination' in config and 'database' in config['destination']:
                        config['destination']['database']['table'] = table_name
                        with open(config_path, 'w') as f:
                            yaml.safe_dump(config, f)
        # --- END NEW ---

        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Error editing target config: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to edit configuration"}), 500

@app.route('/saved-target-configs/<name>', methods=['DELETE'])
def delete_saved_target_config(name):
    try:
        path = os.path.join(BASE_DIR, '../config/saved_target_configs.json')
        if not os.path.exists(path):
            return jsonify({"status": "error", "message": "No configs found"}), 404
        with open(path, 'r') as f:
            configs = json.load(f)
        configs = [c for c in configs if c.get('name', '').strip() != name.strip()]
        with open(path, 'w') as f:
            json.dump(configs, f)
 
        # --- NEW: Clear current target if deleted ---
        current_path = os.path.join(BASE_DIR, '../config/current_config.json')
        if os.path.exists(current_path):
            with open(current_path, 'r') as f:
                current = json.load(f)
            if (current.get('target') or '').strip() == name.strip():
                current['target'] = None
                with open(current_path, 'w') as f:
                    json.dump(current, f)
        # --- END NEW ---
 
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Error deleting target config: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to delete configuration"}), 500

@app.route('/target-configs', methods=['POST'])
def save_target_config():
    try:
        data = request.get_json()
        logger.info(f"Received target config: {data}")
        
        if not data:
            return jsonify({"status": "error", "message": "No JSON data provided"}), 400
            
        target_type = data.get('type')
        table_name = data.get('tableName')
        
        if not table_name:
            return jsonify({"status": "error", "message": "Table name is required"}), 400
        
        # Update both config files
        for config_file in ['../config/api_config.yaml', '../config/ftp_config.yaml']:
            config_path = os.path.join(BASE_DIR, config_file)
            config_path = os.path.abspath(config_path)
            
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    
                if 'destination' in config and 'database' in config['destination']:
                    config['destination']['database']['table'] = table_name
                    with open(config_path, 'w') as f:
                        yaml.safe_dump(config, f)
        
        # Save to saved configs
        path = os.path.join(BASE_DIR, '../config/saved_target_configs.json')
        configs = []
        if os.path.exists(path):
            with open(path, 'r') as f:
                configs = json.load(f)
        configs.append(data)
        with open(path, 'w') as f:
            json.dump(configs, f)
            
        return jsonify({"status": "success", "message": "Destination table updated"}), 200
        
    except Exception as e:
        logger.error(f"Error saving target config: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to save target configuration"}), 500

@app.route('/current-config', methods=['GET'])
def get_current_config():
    path = os.path.join(BASE_DIR, '../config/current_config.json')
    if not os.path.exists(path):
        return jsonify({"source": None, "target": None})
    with open(path, 'r') as f:
        return jsonify(json.load(f))

@app.route('/current-config', methods=['POST'])
def set_current_config():
    data = request.get_json()
    path = os.path.join(BASE_DIR, '../config/current_config.json')
    with open(path, 'w') as f:
        json.dump(data, f)

    # --- Update YAML for current source ---
    source_name = data.get('source')
    if source_name:
        source_configs_path = os.path.join(BASE_DIR, '../config/saved_source_configs.json')
        if os.path.exists(source_configs_path):
            with open(source_configs_path, 'r') as f:
                source_configs = json.load(f)
            current_source = next((c for c in source_configs if c.get('name') == source_name), None)
            if current_source:
                source_type = current_source.get('type', '').upper()
                if source_type == 'API':
                    config_path = os.path.join(BASE_DIR, '../config/api_config.yaml')
                    if os.path.exists(config_path):
                        with open(config_path, 'r') as f:
                            config = yaml.safe_load(f)
                        if 'source' not in config:
                            config['source'] = {}
                        if 'api' not in config['source']:
                            config['source']['api'] = {}
                        if 'auth' not in config['source']['api']:
                            config['source']['api']['auth'] = {}
                        config['source']['api']['url'] = current_source.get('endpoint', '')
                        config['source']['api']['auth']['token'] = current_source.get('authToken', '')
                        retries = current_source.get('retries')
                        if retries is not None:
                            config['source']['api']['retries'] = int(retries)
                        with open(config_path, 'w') as f:
                            yaml.safe_dump(config, f)
                elif source_type == 'FTP':
                    config_path = os.path.join(BASE_DIR, '../config/ftp_config.yaml')
                    if os.path.exists(config_path):
                        with open(config_path, 'r') as f:
                            config = yaml.safe_load(f)
                        if 'source' not in config:
                            config['source'] = {}
                        if 'ftp' not in config['source']:
                            config['source']['ftp'] = {}
                        config['source']['ftp']['host'] = current_source.get('ftpHost', '')
                        config['source']['ftp']['username'] = current_source.get('ftpUsername', '')
                        config['source']['ftp']['password'] = current_source.get('ftpPassword', '')
                        retries = current_source.get('retries')
                        if retries is not None:
                            config['source']['ftp']['retries'] = int(retries)
                        with open(config_path, 'w') as f:
                            yaml.safe_dump(config, f)

    # --- Update YAML for current target ---
    target_name = data.get('target')
    if target_name:
        target_configs_path = os.path.join(BASE_DIR, '../config/saved_target_configs.json')
        if os.path.exists(target_configs_path):
            with open(target_configs_path, 'r') as f:
                target_configs = json.load(f)
            current_target = next((c for c in target_configs if c.get('name') == target_name), None)
            if current_target:
                table_name = current_target.get('tableName')
                target_type = current_target.get('type')
                if target_type == 'Database' and table_name:
                    for yaml_file in ['../config/api_config.yaml', '../config/ftp_config.yaml']:
                        config_path = os.path.join(BASE_DIR, yaml_file)
                        if os.path.exists(config_path):
                            with open(config_path, 'r') as f:
                                config = yaml.safe_load(f)
                            if 'destination' in config and 'database' in config['destination']:
                                config['destination']['database']['table'] = table_name
                                with open(config_path, 'w') as f:
                                    yaml.safe_dump(config, f)

    return jsonify({"status": "success"})

@app.route('/api/profile', methods=['GET'])
def get_profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, email, username, role, last_login
            FROM logins WHERE id = %s
        """, (user_id,))
        user = cur.fetchone()
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        return jsonify({
            'success': True,
            'user': {
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'username': user[3],
                'role': user[4],
                'last_login': user[5].isoformat() if user[5] else None
            }
        })
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)