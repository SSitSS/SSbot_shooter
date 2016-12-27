import matplotlib.pyplot as plt
import numpy as np

num_of_logs = 300

kills, deaths, diffs = {}, {}, {}

for i in range(1, num_of_logs+1):
    with open('logs/'+str(i)+'.log', 'r') as f:
        lines = f.read().split('\n')
        for j in lines:
            words = j.split('\t')
            if words[1] in kills:
                kills[words[1]].append(float(words[2]))
                deaths[words[1]].append(float(words[3]))
                diffs[words[1]].append(float(words[4]))
            else:
                kills[words[1]] = [float(words[2])]
                deaths[words[1]] = [float(words[3])]
                diffs[words[1]] = [float(words[4])]


window = 150
meaned_kills, meaned_deaths, meaned_diffs = {i:[] for i in kills.keys()}, \
                                            {i:[] for i in kills.keys()}, \
                                            {i:[] for i in kills.keys()}
plt.title('SSbot-kills')
plt.hist(kills['SSbot'], bins=np.unique(kills['SSbot']).shape[0])
plt.show()
plt.title('Random-kills')
plt.hist(kills['Random'], bins=np.unique(kills['Random']).shape[0])
plt.show()

plt.title('SSbot-deaths')
plt.hist(deaths['SSbot'], bins=np.unique(deaths['SSbot']).shape[0])
plt.show()
plt.title('Random-deaths')
plt.hist(deaths['Random'], bins=np.unique(deaths['Random']).shape[0])
plt.show()

plt.title('SSbot-diffs')
plt.hist(diffs['SSbot'], bins=np.unique(diffs['SSbot']).shape[0])
plt.show()
plt.title('Random-diffs')
plt.hist(diffs['Random'], bins=np.unique(diffs['Random']).shape[0])
plt.show()



for name in kills:
    #if not name.startswith('Target'):
    for i in range(window, num_of_logs):
        meaned_kills[name].append(sum(kills[name][i+1-window:i+1])/window)
        meaned_deaths[name].append(sum(deaths[name][i + 1 - window:i + 1])/window)
        meaned_diffs[name].append(sum(diffs[name][i + 1 - window:i + 1])/window)


for name in kills:
    plt.plot(range(num_of_logs), kills[name])
plt.legend(kills.keys())
plt.title('Kills')
plt.show()

for name in deaths:
    plt.plot(range(num_of_logs), deaths[name])
plt.legend(deaths.keys())
plt.title('Deaths')
plt.show()

for name in diffs:
    plt.plot(range(num_of_logs), diffs[name])
plt.legend(diffs.keys())
plt.title('Diffs')
plt.show()

for name in meaned_kills:
    print len(meaned_kills[name]), num_of_logs-window
    plt.plot(range(window, num_of_logs), meaned_kills[name])
plt.legend(meaned_kills.keys())
plt.title('Mean kills')
plt.show()

for name in meaned_deaths:
    plt.plot(range(window, num_of_logs), meaned_deaths[name])
plt.legend(deaths.keys())
plt.title('Mean deaths')
plt.show()

for name in meaned_diffs:
    plt.plot(range(window, num_of_logs), meaned_diffs[name])
plt.legend(meaned_diffs.keys())
plt.title('Mean diffs')
plt.show()

