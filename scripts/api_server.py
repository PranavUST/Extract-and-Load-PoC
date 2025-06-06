import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from flask import Flask, request, jsonify
from flask_cors import CORS
from run_pipeline import run_ingestion
from src.logging_utils import setup_logging
import threading
import os

setup_logging("pipeline.log")
print("Current working directory:", os.getcwd())

app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True
)

# Store status in memory for demo purposes
pipeline_status = {"status": "idle", "message": ""}
status_lock = threading.Lock()

def run_pipeline_thread(config_file):
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
        with status_lock:
            pipeline_status["status"] = "error"
            pipeline_status["message"] = str(e)

def _build_cors_preflight_response():
    response = jsonify({"status": "preflight"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

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
