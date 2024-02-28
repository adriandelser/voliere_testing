
# %%
from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from gflow.utils.json_utils import load_from_json
import time
import threading
import requests

# Assuming 'stemlines' is the LineCollection object from the initial ax.stem call
def update_stemlines(stemlines, new_positions):
    segments = []
    for x, y, z in new_positions:
        segment = [(x, y, 0), (x, y, z)]  # Create a segment from base to drone
        segments.append(segment)
    stemlines.set_segments(segments)


# Function to update the plot
def update_plot(frame, plot, ids_ax, d:Drones, stemlines):
    drones = d.drones
    update_stemlines(stemlines, drones[:, :3])
    plot.set_data(drones[:, 0], drones[:, 1])
    plot.set_3d_properties(drones[:, 2])
    # Update text positions
    for i, id in enumerate(ids_ax):
        id.set_position((drones[i, 0], drones[i, 1]))
        id.set_3d_properties(drones[i, 2], zdir='z')
        id.set(text = f"{d.ids[i]}")


    return [plot, *ids]

class Drones:
    def __init__(self, N:int) -> None:
        self.drones = np.full((N,3), np.nan)
        # Add IDs for each drone, for example starting from 01
        self.ids = [f"{i:02d}" for i in range(1, N+1)]
        self.swarm = None

if __name__ == '__main__':
    # Initialize drones
    N = 9  # Number of drones

    d = Drones(N)
    # drones = np.full((N, 3), np.nan)  # Initial positions of the drones

    # Set up the figure and 3D axis
    fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
    x,y,z = d.drones[:, 0], d.drones[:, 1], d.drones[:, 2]

    markerline, stemlines, baseline = ax.stem(x, y, z, linefmt='--', markerfmt='ob', basefmt=' ')

    # Initial plot
    plot, = ax.plot(x,y,z, linestyle=' ', marker='o', color='b')
    # Initialize text annotations for drone IDs
    ids = [ax.text(x[i], y[i], z[i], d.ids[i], color='red') for i in range(N)]

    # Setting the plot limits
    ax.set_xlim([-5, 5])
    ax.set_ylim([-5, 5])
    ax.set_zlim([0, 10])
    #set the axes labels
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    #set the size of the plot to be large
    fig.set_size_inches(8, 8)

    # Creating animation
    ani = FuncAnimation(fig, update_plot, fargs=(plot, ids, d, stemlines), frames=None, interval=20, blit=False, cache_frame_data=False)

    #create a function which updates the positions of drones in a different thread
    def update_positions_thread(d:Drones):
        global stop_position_thread
        url = 'http://127.0.0.1:8000/positions'

        while True:

            try:
                response = requests.get(url)

                if response.status_code == 200:
                    try:
                        positions = response.json()
                        new_positions = np.array([p for id, p in positions.items()])
                        new_ids = [id for id in positions.keys()]
                        # Ensure the new data matches the expected shape
                        if new_positions.ndim == 2 and new_positions.shape[1] == 3:
                            # Update the array in place
                            d.drones = new_positions
                            d.ids = new_ids
                            # print(d.ids)
                        else:
                            print("New positions shape mismatch:", new_positions.shape, "expected:", d.drones.shape)
                    except ValueError as e:
                        print("Response is not in JSON format.")
                        print(e)
                else:
                    print("Error:", response.status_code, response.text)
            except Exception as e:
                print(e.args, "GET request unsuccessful")
            time.sleep(0.01)
            if stop_position_thread:
                break

    #start the thread
    stop_position_thread = False
    pos_thread = threading.Thread(target=update_positions_thread,args=[d])

    pos_thread.start()
    
    plt.show()
    #terminate the thread
    stop_position_thread = True #kill the thread once the plot is closed

    pos_thread.join()


# %%
