import sys
import logging
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from flask import Flask, request, jsonify
from flask_cors import CORS
from run_pipeline import run_ingestion
from src.logging_utils import setup_logging
import threading
import os
from passlib.context import CryptContext
import psycopg2
from psycopg2 import sql
from src.database import get_connection  # Import your connection function
import logging     # Import logger instance
from src.database import create_logins_table_if_not_exists

create_logins_table_if_not_exists()

# Configure logging with absolute path
log_file_path = str(Path(__file__).parent.parent / "pipeline.log")
setup_logging(log_file=log_file_path)

execution_cycle = 0  # Added execution counter
print("Current working directory:", os.getcwd())

app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _build_cors_preflight_response():
    response = jsonify({"status": "preflight"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, password, role FROM logins 
            WHERE username = %s
        """, (username,))
        user = cur.fetchone()
        
        if user and pwd_context.verify(password, user[1]):
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
                "username": username
            })
            
        return jsonify({"success": False}), 401
        
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        return jsonify({"success": False}), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

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

# Store status in memory for demo purposes
pipeline_status = {"status": "idle", "message": ""}
status_lock = threading.Lock()

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
