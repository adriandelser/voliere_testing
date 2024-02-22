from flask import Flask, request, jsonify
import sys
sys.path.append('.')
from common.voliere import VolierePosition
# from common_murat.voliere import Vehicle as Target


import threading




app = Flask(__name__)

# Global variable to store positions
drone_positions = {}






@app.route('/', methods=['GET'])
def hello_world():
    return "hello world"


@app.route('/positions', methods=['GET'])
def get_positions():
    # drone_positions = {tello.ac_id:tello.get_position_enu().tolist() for tello in swarm.tellos}
    
    return jsonify(drone_positions)

@app.route('/positions', methods=['POST'])
def update_positions():
    global drone_positions  # If drone_positions is a global variable
    try:
        data = request.json
        # print(data)
        # Update drone_positions with the new data
        drone_positions.update(data)
        print(drone_positions)
        # Return success message along with the updated positions
        return jsonify({"status": "success", "updated_positions": drone_positions}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
    



