import serial
import time
import matplotlib.pyplot as plt
import csv
from datetime import datetime

SERIAL_PORT = "COM8"
BAUD_RATE = 115200

# 4 antenna orientations
ORIENTATIONS = [
    "Front",
    "Back",
    "Left",
    "Right"
]

MEASURE_TIME = 10  # seconds
ANTENNA = "Horizontal_16.5cm"

# Create timestamp for filenames
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# File names
csv_filename = f"rssi_orientation_data_{ANTENNA}_{timestamp}.csv"
plot_filename = f"rssi_orientation_plot_{ANTENNA}_{timestamp}.png"

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

# =========================
# Data Collection
# =========================

for orientation in ORIENTATIONS:
    print(f"\nRotate robot to: {orientation}")
    print("Push joystick to start recording...")

    # Wait for trigger
    while True:
        line = ser.readline().decode().strip()
        x, rssi = parse_line(line)

        if x is not None and x > 240:
            print(f"Recording {orientation} orientation...")
            break

    # Record RSSI values
    rssi_values = []
    start = time.time()

    while time.time() - start < MEASURE_TIME:
        line = ser.readline().decode().strip()
        x, rssi = parse_line(line)

        if rssi is not None:
            rssi_values.append(rssi)

    results[orientation] = rssi_values
    print(f"Collected {len(rssi_values)} samples")

ser.close()

# =========================
# Save raw RSSI data to CSV
# =========================

with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)

    # Header
    writer.writerow(["Orientation", "Sample_Number", "RSSI_dBm"])

    # Data rows
    for orientation in ORIENTATIONS:
        for i, rssi in enumerate(results[orientation]):
            writer.writerow([orientation, i + 1, rssi])

print(f"\nCSV data saved as: {csv_filename}")

# =========================
# Plotting
# =========================

orientations = []
means = []
mins = []
maxs = []

for orientation in ORIENTATIONS:
    vals = results[orientation]

    if len(vals) == 0:
        continue

    orientations.append(orientation)
    means.append(sum(vals) / len(vals))
    mins.append(min(vals))
    maxs.append(max(vals))

plt.figure(figsize=(8, 5))

# Mean RSSI line
plt.plot(orientations, means, marker='o', label="Average RSSI")

# Error range
plt.fill_between(range(len(orientations)), mins, maxs, alpha=0.2, label="Variation")

plt.xlabel("Orientation")
plt.ylabel("RSSI (dBm)")
plt.title("RSSI vs Orientation")
plt.grid(True)
plt.legend()

plt.tight_layout()

# Save plot
plt.savefig(plot_filename, dpi=300)

print(f"Plot saved as: {plot_filename}")

plt.show()