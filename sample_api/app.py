from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

# Load posts data from JSON file
DATA_FILE = os.path.join(os.path.dirname(__file__), "posts.json")
with open(DATA_FILE, "r") as f:
    posts = json.load(f)

@app.route('/v1/data', methods=['GET'])
def get_posts():
    # Simulate pagination
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 3))
    start = (page - 1) * limit
    end = start + limit
    items = posts[start:end]
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
