
# %%
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from gflow.utils.json_utils import load_from_json
import time
import threading
from drone_monitoring_better import ClientVoliere

# output_data = load_from_json('example_output.json')
# vehicles = output_data['vehicles']
# paths= [v['path'] for v in vehicles]




def update_positions(drones):
    #change the drones array here
    return drones


# Assuming 'stemlines' is the LineCollection object from the initial ax.stem call
def update_stemlines(stemlines, new_positions):
    segments = []
    for x, y, z in new_positions:
        segment = [(x, y, 0), (x, y, z)]  # Create a segment from base to drone
        segments.append(segment)
    stemlines.set_segments(segments)


# Function to update the plot
def update_plot(frame, plot, drones, stemlines):
    update_stemlines(stemlines, drones[:, :3])
    plot.set_data(drones[:, 0], drones[:, 1])
    plot.set_3d_properties(drones[:, 2])
    return plot,

class Drones:
    def __init__(self, N:int) -> None:
        self.drones = np.full((N,3), np.nan)
        self.swarm = None


if __name__ == '__main__':
    # Initialize drones
    N = 4  # Number of drones

    d = Drones(N)
    # drones = np.full((N, 3), np.nan)  # Initial positions of the drones

    # Set up the figure and 3D axis
    fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
    x,y,z = d.drones[:, 0], d.drones[:, 1], d.drones[:, 2]
    markerline, stemlines, baseline = ax.stem(x, y, z, linefmt='--', markerfmt='ob', basefmt=' ')

    # Initial plot
    plot, = ax.plot(x,y,z, linestyle=' ', marker='o', color='b')

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
    ani = FuncAnimation(fig, update_plot, fargs=(plot, d.drones, stemlines), frames=None, interval=20, blit=False, cache_frame_data=False)

    # #create a function which updates the positions of drones in a different thread
    # def update_positions_thread():
    #     global stop_thread
    #     while True:
    #         update_positions(d.drones)
    #         time.sleep(0.01)
    #         if stop_thread:
    #             break

    #start the thread
    # stop_thread = False
    # thread = threading.Thread(target=update_positions_thread)
    # thread.start()
    vvt = ClientVoliere(d)

    # Start the ClientVoliere in a separate thread
    threading.Thread(target=vvt.start, daemon=True).start()
    # threading.Thread(target=print, daemon=True).start()

    plt.show()
    #terminate the thread
    # stop_thread = True #kill the thread once the plot is closed
    # thread.join()


# %%
