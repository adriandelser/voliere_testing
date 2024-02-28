from vispy import scene
from vispy import app
from vispy.scene import visuals
import numpy as np
import threading
import requests
import time

class RealTimePlotter:
    def __init__(self, N):
        # Set up VisPy canvas
        self.canvas = scene.SceneCanvas(keys='interactive', show=True)
        self.view = self.canvas.central_widget.add_view()
        
        # Set up 3D axis
        self.view.camera = 'turntable'  # or try 'arcball'
        
        # Initialize drone positions and visuals
        self.N = N
        self.positions = np.zeros((N, 3))
        self.lines = [visuals.Line(pos=np.array([[0, 0, 0], [0, 0, 0]]), color='blue', parent=self.view.scene) for _ in range(N)]
        self.spheres = [visuals.Sphere(radius=0.1, edges=20, color='red', parent=self.view.scene) for _ in range(N)]
        
        # Update visuals to current positions
        self.update_visuals()

    def update_positions(self, new_positions):
        self.positions = new_positions
        self.update_visuals()

    def update_visuals(self):
        for i in range(self.N):
            pos = self.positions[i]
            # Update lines (stems)
            self.lines[i].set_data(np.array([[pos[0], pos[1], 0], pos]))
            # Update spheres (drone positions)
            self.spheres[i].transform = visuals.transforms.STTransform(translate=pos)

def fetch_positions(d_plotter):
    url = 'http://127.0.0.1:8000/positions'
    while not stop_position_thread:
        response = requests.get(url)
        if response.status_code == 200:
            try:
                positions = response.json()
                new_positions = np.array([p for id, p in positions.items()])
                d_plotter.update_positions(new_positions)
            except Exception as e:
                print("Error updating positions:", e)
        time.sleep(0.01)

if __name__ == '__main__':
    N = 4  # Number of drones
    plotter = RealTimePlotter(N)
    
    stop_position_thread = False
    position_thread = threading.Thread(target=fetch_positions, args=(plotter,))
    position_thread.start()

    # Start the VisPy application
    app.run()

    # Stop the position fetching thread
    stop_position_thread = True
    position_thread.join()
