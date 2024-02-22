import matplotlib.pyplot as plt
import numpy as np

N = 10  # Number of drones
drones = np.zeros((N,3))
#randomise the positions of the drones within a 5x5x5 cube
for i in range(N):
    drones[i, 0] = np.random.uniform(-5, 5)
    drones[i, 1] = np.random.uniform(-5, 5)
    drones[i, 2] = np.random.uniform(0, 10)

#plot the positions of the drones
x = drones[:, 0]
y = drones[:, 1]
z = drones[:, 2]


fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
ax.stem(x, y, z, linefmt='--', markerfmt='ob', basefmt=' ')

# Adjusting the plot range
ax.set_xlim([-5, 5])  # Setting x-axis limits
ax.set_ylim([-5, 5])  # Setting y-axis limits
ax.set_zlim([0, 10])       # Setting z-axis limits

plt.show()