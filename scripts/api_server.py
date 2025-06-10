import sys
import yaml
import json
import logging
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from flask import Flask, request, jsonify
from flask_cors import CORS
from run_pipeline import run_ingestion
from src.logging_utils import setup_logging
import threading
import os

# Set up logger
logger = logging.getLogger(__name__)

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
        logger.error(f"Pipeline execution failed: {str(e)}")
        with status_lock:  # Maintain thread safety for error status
            pipeline_status["status"] = "error"
            pipeline_status["message"] = str(e)
    finally:
        logging.info("-" * 80)  # Add separator after each execution

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
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON data provided"}), 400
            
        config_file = data.get("config_file")
        if not config_file:
            return jsonify({"status": "error", "message": "No config file provided"}), 400
        
        threading.Thread(target=run_pipeline_thread, args=(config_file,), daemon=True).start()
        return jsonify({"status": "started"})
    except Exception as e:
        logger.error(f"Error starting pipeline: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to start pipeline"}), 500

@app.route('/pipeline-status', methods=['GET'])
def get_status():
    with status_lock:
        return jsonify(pipeline_status)

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
        configs = [c for c in configs if c.get('name') != name]
        with open(path, 'w') as f:
            json.dump(configs, f)

        # --- NEW: Clear current source if deleted ---
        current_path = os.path.join(BASE_DIR, '../config/current_config.json')
        if os.path.exists(current_path):
            with open(current_path, 'r') as f:
                current = json.load(f)
            print(f"Deleting: {name}, Current source: {current.get('source')}")
            if current.get('source') == name:
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
        configs = [c for c in configs if c.get('name') != name]
        with open(path, 'w') as f:
            json.dump(configs, f)

        # --- NEW: Clear current target if deleted ---
        current_path = os.path.join(BASE_DIR, '../config/current_config.json')
        if os.path.exists(current_path):
            with open(current_path, 'r') as f:
                current = json.load(f)
            if current.get('target') == name:
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)