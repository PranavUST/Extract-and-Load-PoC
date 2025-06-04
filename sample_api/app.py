from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "posts.json")

def load_posts():
    """Load posts from JSON file on each request"""
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        app.logger.error(f"Error loading posts.json: {e}")
        return []

@app.route('/v1/data', methods=['GET'])
def get_posts():
    # Load fresh data on each request
    posts = load_posts()
    
    # Simulate pagination
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 3))
    start = (page - 1) * limit
    end = start + limit
    items = posts[start:end]
    
    app.logger.info(f"Serving {len(items)} items from {len(posts)} total posts")
    
    return jsonify({
        "data": {
            "items": items
        },
        "meta": {
            "total": len(posts),
            "page": page,
            "limit": limit
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)