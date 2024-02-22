
# %%
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
# from mpl_toolkits.mplot3d import Axes3D
# from gflow.utils.json_utils import load_from_json
import time
import threading



# Initialize drones
N = 10  # Number of drones
drones = np.full((N, 3), np.nan)  # Initial positions of the drones

# Set up the figure and 3D axis
fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
x,y,z = drones[:, 0], drones[:, 1], drones[:, 2]
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

# Assuming 'stemlines' is the LineCollection object from the initial ax.stem call
def update_stemlines(stemlines, new_positions):
    segments = []
    for x, y, z in new_positions:
        segment = [(x, y, 0), (x, y, z)]  # Create a segment from base to drone
        segments.append(segment)
    stemlines.set_segments(segments)


# Function to update drone positions randomly
def update_positions(drones):
    for i in range(N):
        drones[i, 0] = np.random.uniform(-5, 5)
        drones[i, 1] = np.random.uniform(-5, 5)
        drones[i, 2] = np.random.uniform(0, 10)
    return drones

# Function to update the plot
def update_plot(frame, plot, stemlines):
    # ax.cla()
    # new_positions = update_positions(drones)
    # Update stemlines with new positions
    # update_stemlines(stemlines, new_positions[:, :3])
    update_stemlines(stemlines, drones[:, :3])
    plot.set_data(drones[:, 0], drones[:, 1])
    plot.set_3d_properties(drones[:, 2])
    return plot,


# Creating animation
ani = FuncAnimation(fig, update_plot, fargs=(plot, stemlines), frames=None, interval=20, blit=False, cache_frame_data=False)

#create a function which updates the positions of drones in a different thread
def update_positions_thread():
    while True:
        update_positions(drones)
        # print(drones)
        time.sleep(0.1)

#start the thread
i = 0
thread = threading.Thread(target=update_positions_thread)
thread.start()

plt.show()
#terminate the thread
thread.join()


# %%
