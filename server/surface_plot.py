from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import threading
import time
from gflow.utils.json_utils import load_from_json
import requests


#FIXME THIS IS SLOW, clearing and redrawing is not the way, pause for now

# output_data = load_from_json('example_output.json')
# vehicles = output_data['vehicles']
# paths= [v['path'] for v in vehicles]
# paths = [(np.array(path)+np.array([0,0,4])).tolist() for path in paths]




# def update_stemlines_and_paths(paths_history):
#     global surface_collections, drone_path_vertices, path_plots
#     for idx, history in enumerate(paths_history):
#         # Update path plot
#         path_plots[idx].set_data(history[:, 0], history[:, 1])
#         path_plots[idx].set_3d_properties(history[:, 2])
        
#         if np.count_nonzero(~np.isnan(history[:, 0])) > 1:
#             # Get the index of the last valid point
#             valid_indices = np.where(~np.isnan(history[:, 0]))[0]
#             if len(valid_indices) > 1:
#                 new_point_idx = valid_indices[-1]
#                 prev_point_idx = valid_indices[-2]

#                 # Create vertices for the new segment
#                 new_segment_verts = [[history[prev_point_idx, :2].tolist() + [0], 
#                                       history[new_point_idx, :2].tolist() + [0],
#                                       history[new_point_idx, :].tolist(), 
#                                       history[prev_point_idx, :].tolist()]]

#                 # Update the vertices list for this drone
#                 # If the list is at max capacity, remove the oldest segment
#                 if len(drone_path_vertices[idx]) >= history_length:
#                     drone_path_vertices[idx].pop(0)
#                 drone_path_vertices[idx].append(new_segment_verts[0])
                
#                 # Update the Poly3DCollection with the new set of vertices
#                 surface_collections[idx].set_verts(drone_path_vertices[idx])

def update_stemlines_and_paths(paths_history):
    global surface_collections, drone_path_vertices, path_plots
    for idx, history in enumerate(paths_history):
        # Update path plot
        path_plots[idx].set_data(history[:, 0], history[:, 1])
        path_plots[idx].set_3d_properties(history[:, 2])

        # Check if there are at least two points to form a segment
        if np.count_nonzero(~np.isnan(history[:, 0])) > 1:
            valid_indices = np.where(~np.isnan(history[:, 0]))[0]
            if len(valid_indices) > 1:
                # Generate new vertices based off the paths_history
                new_vertices = []
                for i in range(len(valid_indices) - 1):
                    prev_point_idx = valid_indices[i]
                    new_point_idx = valid_indices[i + 1]

                    # Create vertices for the new segment
                    new_segment_verts = [[history[prev_point_idx, :2].tolist() + [0], 
                                          history[new_point_idx, :2].tolist() + [0],
                                          history[new_point_idx, :].tolist(), 
                                          history[prev_point_idx, :].tolist()]]
                    new_vertices.extend(new_segment_verts)

                # Update the vertices list for this drone directly with the new vertices
                drone_path_vertices[idx] = new_vertices
                
                # Update the Poly3DCollection with the new set of vertices
                surface_collections[idx].set_verts(new_vertices)
# Function to update the plot
def update_plot(frame, plot, ids_ax, d:Drones):
    drones = d.drones
    paths_history = d.paths
    # update_stemlines(stemlines, drones[:, :3])
    plot.set_data(drones[:, 0], drones[:, 1])
    plot.set_3d_properties(drones[:, 2])
    update_stemlines_and_paths(paths_history)

    # Update text positions
    for i, id in enumerate(ids_ax):
        id.set_position((drones[i, 0], drones[i, 1]))
        id.set_3d_properties(drones[i, 2], zdir='z')
        id.set(text = f"{d.ids[i]}")
    
    return [plot, *ids]

class Drones:
    def __init__(self, N) -> None:
        # N = len(id_list)
        self.drones = np.full((N,3), np.nan)
        self.paths = np.full((N,100,3), np.nan)
        # Add IDs for each drone, for example starting from 01
        self.ids = [f"{i:02d}" for i in range(1, N+1)]
        self.swarm = None

def update_positions_thread(d:Drones):
        global stop_position_thread
        url = 'http://127.0.0.1:8000/positions'

        while True:

            try:
                response = requests.get(url)

                if response.status_code == 200:
                    try:
                        positions = response.json()
                        new_positions = np.array([p for id, p in positions.items()]) + np.array([0,0,0])
                        new_ids = [id for id in positions.keys()]
                        # Ensure the new data matches the expected shape
                        if new_positions.ndim == 2 and new_positions.shape[1] == 3:
                            # Update the array in place
                            d.drones = new_positions
                            d.ids = new_ids
                        else:
                            print("New positions shape mismatch:", new_positions.shape, "expected:", d.drones.shape)
                    except ValueError as e:
                        print("Response is not in JSON format.")
                        print(e)
                else:
                    print("Error:", response.status_code, response.text)
            except Exception as e:
                print(e.args, "GET request unsuccessful")
            time.sleep(0.05)
            if stop_position_thread:
                break

def update_paths_thread(d:Drones):
        global stop_paths_thread
        url = 'http://127.0.0.1:8000/paths'

        while True:

            try:
                response = requests.get(url)

                if response.status_code == 200:
                    try:
                        paths = response.json()
                        new_paths = np.array([p for id, p in paths.items()])+np.array([0,0,0])

                        # new_ids = [id for id in positions.keys()]
                        # Ensure the new data matches the expected shape
                        if new_paths.ndim == 3 and new_paths.shape[2] == 3:
                            # Update the array in place
                            d.paths = new_paths
                        else:
                            print("New paths shape mismatch:", new_paths.shape, "expected:", d.paths.shape)
                    except ValueError as e:
                        print("Response is not in JSON format.")
                        print(e)
                else:
                    print("Error:", response.status_code, response.text)
            except Exception as e:
                print(e.args, "GET request unsuccessful")
            time.sleep(0.05)
            if stop_paths_thread:
                break

if __name__ == "__main__":
    # Initialize drones
    N = 2  # Number of drones
    d = Drones(N)
    #start the thread
    stop_position_thread = False
    stop_paths_thread = False
    paths = [[] for _ in range(N)]
    drones = np.full((N, 3), np.nan)  # Initial positions of the drones
    history_length = 100  # Number of past points to visualize
    paths_history = [np.full((history_length, 3), np.nan) for _ in range(N)]  # History of positions for each drone

    # Set up the figure and 3D axis
    fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
    x,y,z = d.drones[:, 0], d.drones[:, 1], d.drones[:, 2]
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
    colours = ['r','b','g','k','c']
    path_plots = [ax.plot([], [], [], f'{colours[_%len(colours)]}-')[0] for _ in range(N)]
    # Initialize text annotations for drone IDs
    ids = [ax.text(x[i], y[i], z[i], d.ids[i], color='red') for i in range(N)]


    # Initialize one Poly3DCollection per drone for the surface
    surface_collections = [Poly3DCollection([], alpha=0.25) for _ in range(N)]
    for idx, poly in enumerate(surface_collections):
        poly.set_facecolor(colours[idx%len(colours)])
        ax.add_collection3d(poly)
    #         
    # Initialize an external structure to manage vertices for each drone
    # This will hold the current vertices for the visible segments of the path
    drone_path_vertices = [[] for _ in range(N)]
    i = 1
    # Creating animation
    ani = FuncAnimation(fig, update_plot, fargs=(plot, ids, d), frames=None, interval=100, blit=False, cache_frame_data=False)

    pos_thread = threading.Thread(target=update_positions_thread,args=[d])
    paths_thread = threading.Thread(target=update_paths_thread, args=[d])
    pos_thread.start()
    paths_thread.start()
    plt.show()
    
    #terminate the thread
    stop_position_thread = True #kill the thread once the plot is closed
    stop_paths_thread = True
    pos_thread.join()
    paths_thread.join()
