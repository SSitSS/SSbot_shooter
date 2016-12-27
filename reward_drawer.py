import matplotlib.pyplot as plt
import numpy as np

episodes = 2425

mean_rewards = []
all_rewards = []

name = 'DQN5'

for i in range(1, episodes+1):
    with open('rewards_log/' + name + str(i) + '.log', 'r') as f:
        rwds = [float(j) for j in f.read().split()]
    if rwds:
        all_rewards += rwds
        mean_rewards.append(sum(rwds)/len(rwds))
    else:
        mean_rewards.append(-1)

points = range(1, len(all_rewards)+1)
plt.plot(points, all_rewards)
plt.title('all')
z = np.polyfit(points, all_rewards, 2)
p = np.poly1d(z)
plt.plot(points, p(points), "r", lw=3)
plt.show()

points = range(1, len(mean_rewards)+1)
plt.plot(points, mean_rewards)
z = np.polyfit(points, mean_rewards, 2)
p = np.poly1d(z)
plt.plot(points, p(points), "r", lw=3)
plt.title('mean')
plt.show()

window = 10000
rw = np.array(all_rewards)
size = rw.shape[0]/window*window
print size
rw = rw[:size]
size /= window
rw = rw.reshape((size, window))
points = range(size)
slope_rewards = [np.mean(rw[i]) for i in points]
plt.plot(points, slope_rewards)
plt.title('average')
z = np.polyfit(points, slope_rewards, 2)
p = np.poly1d(z)
plt.plot(points, p(points), "r", lw=3)
plt.show()