#%%
import matplotlib.pyplot as plt
import numpy as np

X, Y = np.meshgrid(np.linspace(0, 10,10), np.linspace(0, 10,10))
q = plt.quiver(X, Y , np.random.rand(10, 10), np.random.rand(10, 10))
#set axis limits in y to -5 to 10
plt.ylim(-5, 10)
plt.draw()
plt.pause(2)
# print(q.get_positions())
q.set_offsets(q.get_offsets() - np.array([0, 5]))
plt.draw()
plt.pause(10)



# %%
