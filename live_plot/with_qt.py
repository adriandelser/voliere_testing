import sys
import numpy as np
import pyqtgraph.opengl as gl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

class DroneVisualizer:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = gl.GLViewWidget()
        self.window.setWindowTitle('Real-time Drone Visualization')
        self.window.setGeometry(0, 110, 800, 600)
        self.window.show()

        # Create a grid floor
        grid = gl.GLGridItem()
        grid.scale(10, 10, 1)
        self.window.addItem(grid)

        # Initialize drone path history and marker
        self.N = 4  # Number of drones
        self.drone_paths = [np.empty((0,3)) for _ in range(self.N)]
        self.drone_markers = [gl.GLScatterPlotItem(pos=np.random.rand(1,3)*10, color=(i/self.N,1-i/self.N,0.5,0.5), size=0.5) for i in range(self.N)]
        for marker in self.drone_markers:
            self.window.addItem(marker)

        # Timer for updating positions
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_positions)
        self.timer.start(100)  # Update interval in milliseconds

    def update_positions(self):
        # Simulate new positions (replace this with actual data fetching)
        new_positions = np.random.rand(self.N, 3) * 20 - 10

        for i in range(self.N):
            # Update path history
            self.drone_paths[i] = np.vstack((self.drone_paths[i], new_positions[i]))
            if len(self.drone_paths[i]) > 100:  # Keep last 100 points
                self.drone_paths[i] = self.drone_paths[i][1:]

            # Update markers
            self.drone_markers[i].setData(pos=new_positions[i:i+1])

    def start(self):
        sys.exit(self.app.exec_())

if __name__ == '__main__':
    visualizer = DroneVisualizer()
    visualizer.start()
