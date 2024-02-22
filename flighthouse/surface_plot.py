import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import threading
import time
from gflow.utils.json_utils import load_from_json

#FIXME THIS IS SLOW, clearing and redrawing is not the way, pause for now

output_data = load_from_json('example_output.json')
vehicles = output_data['vehicles']
paths= [v['path'] for v in vehicles]
paths = [(np.array(path)+np.array([0,0,4])).tolist() for path in paths]

# # Dummy function for loading data
# def load_from_json(filename):
#     return {
#         'vehicles': [{'path': [[0, 0, 1], [1, 1, 1], [2, 2, 1], [3, 3, 1]]}]
#     }

# output_data = load_from_json('example_output.json')
# vehicles = output_data['vehicles']
# paths = [v['path'] for v in vehicles]

# Initialize drones
N = len(paths)  # Number of drones
drones = np.full((N, 3), np.nan)  # Initial positions of the drones
history_length = 30  # Number of past points to visualize
paths_history = [np.full((history_length, 3), np.nan) for _ in range(N)]  # History of positions for each drone

# Set up the figure and 3D axis
fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
ax.set_xlim([-5, 5])
ax.set_ylim([-5, 5])
ax.set_zlim([0, 10])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
fig.set_size_inches(8, 8)

# Initial plot for drones
plot, = ax.plot([], [], [], linestyle=' ', marker='o', color='b')

# Initial plot for paths
path_plots = [ax.plot([], [], [], 'r-')[0] for _ in range(N)]

# Initialize a list to keep track of surface collections
surface_collections = []

def update_stemlines_and_paths(drones, paths_history):
    global surface_collections
    
    # Remove old surfaces
    for col in surface_collections:
        col.remove()
    surface_collections.clear()
    
    # Update paths and add new surfaces
    for idx, history in enumerate(paths_history):
        # Update path plot
        path_plots[idx].set_data(history[:, 0], history[:, 1])
        path_plots[idx].set_3d_properties(history[:, 2])
        
        # Draw surfaces for the current path history
        for i in range(1, len(history)):
            verts = [[history[i-1, :2].tolist() + [0], history[i, :2].tolist() + [0],
                      history[i, :].tolist(), history[i-1, :].tolist()]]
            poly = Poly3DCollection(verts, facecolors='cyan', linewidths=1, edgecolors='none', alpha=.25)
            ax.add_collection3d(poly)
            surface_collections.append(poly)


def update_positions(drones, paths_history):
    global i 
    for idx, path in enumerate(paths):
        current_position = path[i % len(path)]
        drones[idx, :3] = current_position
        # Update history
        paths_history[idx] = np.roll(paths_history[idx], -1, axis=0)
        paths_history[idx][-1, :] = current_position
    i += 1
    return drones

# Function to update the plot
def update_plot(frame, plot, drones, paths_history):
    drones = update_positions(drones, paths_history)
    plot.set_data(drones[:, 0], drones[:, 1])
    plot.set_3d_properties(drones[:, 2])
    update_stemlines_and_paths(drones, paths_history)
    return plot,

i = 1
# Creating animation
ani = FuncAnimation(fig, update_plot, fargs=(plot, drones, paths_history), frames=None, interval=50, blit=False, cache_frame_data=False)

plt.show()
