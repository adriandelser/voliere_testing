from flask import Flask, request, jsonify
import sys
sys.path.append('.')
# from common.voliere import VolierePosition
from collections import deque
# from common_murat.voliere import Vehicle as Target


import threading




app = Flask(__name__)

# Global variable to store positions
drone_positions = {}
drone_paths = {}
desired_vectors = {}






@app.route('/', methods=['GET'])
def hello_world():
    return "hello world"


@app.route('/positions', methods=['GET'])
def get_positions():
    return jsonify(drone_positions)

@app.route('/paths', methods=['GET'])
def get_paths():
    # Convert each deque in drone_paths to a list for JSON serialization
    paths_as_lists = {drone_id: list(path) for drone_id, path in drone_paths.items()}
    return jsonify(paths_as_lists)


@app.route('/positions', methods=['POST'])
def update_positions():
    global drone_positions  # If drone_positions is a global variable
    global drone_paths
    try:
        data = request.json
        # print(data)
        # Update drone_positions with the new data
        drone_positions.update(data)
        print(drone_positions)
        for drone_id, position in data.items():
            # Update paths
            if drone_id not in drone_paths:
                # If the drone is not already in drone_paths, initialize its path with a deque
                drone_paths[drone_id] = deque(maxlen=100)
            # Append the new position and automatically maintain the size limit
            drone_paths[drone_id].append(position)
        # Return success message along with the updated positions
        return jsonify({"status": "success", "updated_positions": drone_positions}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/desired', methods=['GET'])
def get_desired():    
    return jsonify(desired_vectors)
    
@app.route('/desired', methods=['POST'])
def update_desired():
    global desired_vectors  # If drone_positions is a global variable
    try:
        data = request.json
        # print(data)
        # Update drone_positions with the new data
        desired_vectors.update(data)
        # print(drone_positions)
        # Return success message along with the updated positions
        return jsonify({"status": "success", "updated_positions": desired_vectors}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
    



