import serial
import time
import matplotlib.pyplot as plt
import csv
from datetime import datetime

SERIAL_PORT = "COM8"
BAUD_RATE = 115200

DISTANCES = [1, 5, 10, 20, 40]  # meters
MEASURE_TIME = 10  # seconds
ANTENNA = "Horizontal_16.5cm"

# Create timestamp for filenames
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# File names
csv_filename = f"rssi_data_{ANTENNA}_{timestamp}.csv"
plot_filename = f"rssi_plot_{ANTENNA}_{timestamp}.png"

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)

results = {}

def parse_line(line):
    try:
        parts = line.split(",")
        x = int(parts[0].split(":")[1])
        rssi = int(parts[1].split(":")[1])
        return x, rssi
    except:
        return None, None

for dist in DISTANCES:
    print(f"\nMove to {dist} meters. Push joystick to start...")

    # Wait for trigger
    while True:
        line = ser.readline().decode().strip()
        x, rssi = parse_line(line)

        if x is not None and x > 240:
            print(f"Recording at {dist} m...")
            break

    # Record for MEASURE_TIME seconds
    rssi_values = []
    start = time.time()

    while time.time() - start < MEASURE_TIME:
        line = ser.readline().decode().strip()
        x, rssi = parse_line(line)

        if rssi is not None:
            rssi_values.append(rssi)

    results[dist] = rssi_values
    print(f"Collected {len(rssi_values)} samples")

ser.close()

# =========================
# Save raw RSSI data to CSV
# =========================

with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)

    # Header
    writer.writerow(["Distance_m", "Sample_Number", "RSSI_dBm"])

    # Data rows
    for dist in DISTANCES:
        for i, rssi in enumerate(results[dist]):
            writer.writerow([dist, i + 1, rssi])

print(f"\nCSV data saved as: {csv_filename}")

# =========================
# Plotting
# =========================

distances = []
means = []
mins = []
maxs = []

for d in DISTANCES:
    vals = results[d]

    if len(vals) == 0:
        continue

    distances.append(d)
    means.append(sum(vals) / len(vals))
    mins.append(min(vals))
    maxs.append(max(vals))

plt.figure()

# Mean RSSI line
plt.plot(distances, means, marker='o', label="Average RSSI")

# Error bars (min/max spread)
plt.fill_between(distances, mins, maxs, alpha=0.2, label="Variation")

plt.xlabel("Distance (m)")
plt.ylabel("RSSI (dBm)")
plt.title("RSSI vs Distance")
plt.grid(True)
plt.legend()

plt.tight_layout()

# Save plot
plt.savefig(plot_filename, dpi=300)

print(f"Plot saved as: {plot_filename}")

plt.show()