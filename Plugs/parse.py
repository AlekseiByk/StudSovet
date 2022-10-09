import matplotlib.pyplot as plt
import datetime
import time

date = datetime.datetime.now().date()
log_file = open(f"logs/Plugs{date}.log", "r")
Lines = log_file.readlines()

number_of_plugs = 7
x = [[]*number_of_plugs]
y = [[]*number_of_plugs]
for line in Lines:
    obj = datetime.datetime.strptime(line.split(' ')[0] + " " + line.split(' ')[1], "%Y-%m-%d %H:%M:%S,%f")
    sec = obj.time().hour * 60 * 60 + obj.time().minute * 60 + obj.time().second
    x[int(line.split(' ')[4]) - 1].append(sec/3600)
    y[int(line.split(' ')[4]) - 1].append(int(line.split(' ')[9]))

for x_cord in x:
    plt.figure(figsize=[48, 16], dpi=120)
    plt.plot(x_cord, y[i], label = f"washer {i + 1}")
    for x_x in range(12):
        plt.axvline(x_x * 2, color = "r")
    plt.xlabel('время, сек')
    plt.ylabel('ток, мА')
    plt.xticks(range(25))
    plt.savefig(f'output/plot{date}_{i+1}.png')
    i += 1

plt.show()

