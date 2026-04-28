import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import time

SERIAL_PORT = "COM8"
BAUD_RATE = 115200
MAX_POINTS = 200

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)

rssi_values = deque(maxlen=MAX_POINTS)
time_values = deque(maxlen=MAX_POINTS)
start_time = time.time()

fig, ax = plt.subplots()
line, = ax.plot([], [], 'b-')

ax.set_ylim(-120, 0)
ax.set_xlabel("Time (s)")
ax.set_ylabel("RSSI (dBm)")
ax.set_title("RSSI over time")
ax.grid(True)

def update(frame):
    if time.time() - start_time > 20:
        ani.event_source.stop()
        ser.close()
        return line,

    while ser.in_waiting:
        raw = ser.readline().decode("utf-8", errors="replace").strip()
        if raw.startswith("RSSI:"):
            try:
                val = int(raw.split(":")[1].strip())
                rssi_values.append(val)
                time_values.append(time.time() - start_time)
            except:
                pass

    line.set_data(list(time_values), list(rssi_values))
    ax.set_xlim(0, 20)
    return line,

ani = animation.FuncAnimation(fig, update, interval=100)
plt.tight_layout()
plt.show()