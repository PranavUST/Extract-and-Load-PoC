import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
# ...existing code...
from flask import Flask, request, jsonify
from flask_cors import CORS
from run_pipeline import run_ingestion
from src.logging_utils import setup_logging
log_file_path = str(Path(__file__).parent.parent / "pipeline.log")
setup_logging(log_file=log_file_path)
import threading
import os
print("Current working directory:", os.getcwd())

app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True
)
# Store status in memory for demo purposes
pipeline_status = {"status": "idle", "message": ""}

def run_pipeline_thread(config_file):
    try:
        if not os.path.isabs(config_file):
            config_file = str(Path(__file__).parent.parent / config_file)
        pipeline_status["status"] = "running"
        pipeline_status["message"] = "Pipeline is running"
        run_ingestion(config_file)
        pipeline_status["status"] = "success"
        pipeline_status["message"] = "Pipeline completed successfully"
    except Exception as e:
        pipeline_status["status"] = "error"
        pipeline_status["message"] = str(e)

@app.route('/run-pipeline', methods=['POST'])
def run_pipeline_api():
    data = request.get_json()
    config_file = data.get("config_file")
    if not config_file:
        return jsonify({"status": "error", "message": "No config file provided"}), 400
    # Start pipeline in a background thread
    threading.Thread(target=run_pipeline_thread, args=(config_file,), daemon=True).start()
    return jsonify({"status": "started"})
# ...existing code...

@app.route('/pipeline-status', methods=['GET'])
def get_status():
    return jsonify(pipeline_status)

@app.route('/v1/data', methods=['GET'])
def get_data():
    # Replace with your real data logic
    return jsonify([])

if __name__ == "__main__":
    app.run(port=5000)