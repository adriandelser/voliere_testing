
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
# from drone_monitoring_better import ClientVoliere

# output_data = load_from_json('example_output.json')
# vehicles = output_data['vehicles']
# paths= [v['path'] for v in vehicles]




# def update_positions(drones):
#     #change the drones array here
#     return drones


# Assuming 'stemlines' is the LineCollection object from the initial ax.stem call
def update_stemlines(stemlines, new_positions):
    segments = []
    for x, y, z in new_positions:
        segment = [(x, y, 0), (x, y, z)]  # Create a segment from base to drone
        segments.append(segment)
    stemlines.set_segments(segments)


# Function to update the plot
def update_plot(frame, plot, d:Drones, stemlines):
    drones = d.drones
    update_stemlines(stemlines, drones[:, :3])
    plot.set_data(drones[:, 0], drones[:, 1])
    plot.set_3d_properties(drones[:, 2])
    return plot,

class Drones:
    def __init__(self, N:int) -> None:
        self.drones = np.full((N,3), np.nan)
        self.desired = np.full((N,3), np.nan)
        self.swarm = None


if __name__ == '__main__':
    # Initialize drones
    N = 4  # Number of drones

    d = Drones(N)
    # drones = np.full((N, 3), np.nan)  # Initial positions of the drones

    # Set up the figure and 3D axis
    fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
    x,y,z = d.drones[:, 0], d.drones[:, 1], d.drones[:, 2]
    u, v, w = d.desired[:, 0], d.vectors[:, 1], d.vectors[:, 2]  # Direction vectors

    markerline, stemlines, baseline = ax.stem(x, y, z, linefmt='--', markerfmt='ob', basefmt=' ')

    # Initial plot
    plot, = ax.plot(x,y,z, linestyle=' ', marker='o', color='b')
    # Adding arrows to indicate direction
    ax.quiver(x, y, z, u, v, w, length=0.5, normalize=True)

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
    ani = FuncAnimation(fig, update_plot, fargs=(plot, d, stemlines), frames=None, interval=20, blit=False, cache_frame_data=False)

    #create a function which updates the positions of drones in a different thread
    def update_positions_thread(d:Drones):
        global stop_position_thread
        url = 'http://127.0.0.1:8000/positions'

        while True:
            response = requests.get(url)

            if response.status_code == 200:
                try:
                    positions = response.json()
                    new_positions = np.array([p for id, p in positions.items()])
                    # Ensure the new data matches the expected shape
                    if new_positions.ndim == 2 and new_positions.shape[1] == 3:
                        # Update the array in place
                        d.drones = new_positions
                    else:
                        print("New positions shape mismatch:", new_positions.shape, "expected:", d.drones.shape)
                except ValueError as e:
                    print("Response is not in JSON format.")
                    print(e)
            else:
                print("Error:", response.status_code, response.text)
            time.sleep(0.01)
            if stop_position_thread:
                break
    # #create a function which updates the desired vectors of drones in a different thread
    # def update_vectors_thread(d:Drones):
    #     global stop_vector_thread
    #     url = 'http://127.0.0.1:8000/vectors'

    #     while True:
    #         response = requests.get(url)

    #         if response.status_code == 200:
    #             try:
    #                 vectors = response.json()
    #                 new_vectors = np.array([p for id, p in vectors.items()])
    #                 # Ensure the new data matches the expected shape
    #                 if new_vectors.ndim == 2 and new_vectors.shape[1] == 3:
    #                     # Update the array in place
    #                     d.desired = new_vectors
    #                 else:
    #                     print("New positions shape mismatch:", new_vectors.shape, "expected:", d.drones.shape)
    #             except ValueError as e:
    #                 print("Response is not in JSON format.")
    #                 print(e)
    #         else:
    #             print("Error:", response.status_code, response.text)
    #         time.sleep(0.01)
    #         if stop_position_thread:
    #             break
    #start the thread
    stop_position_thread = False
    stop_vector_thread = False
    pos_thread = threading.Thread(target=update_positions_thread,args=[d])
    vec_thread = threading.Thread(target=update_vectors_thread,args=[d])

    pos_thread.start()
    vec_thread.start()
    
    plt.show()
    #terminate the thread
    stop_position_thread = True #kill the thread once the plot is closed
    stop_vector_thread = True #kill the thread once the plot is closed

    pos_thread.join()


# %%
