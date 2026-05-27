import serial
import time
import matplotlib.pyplot as plt
import csv
import re
from datetime import datetime

# =========================
# SETTINGS
# =========================

SERIAL_PORT = "COM8"
BAUD_RATE = 115200

BITRATE_LABEL = "1.2 kbps"   # Change this manually for each test
MEASURE_TIME = 10           # seconds

# =========================
# FILE SETUP
# =========================

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

csv_filename = f"latency_{BITRATE_LABEL.replace(' ', '_')}_{timestamp}.csv"
plot_filename = f"latency_{BITRATE_LABEL.replace(' ', '_')}_{timestamp}.png"

# =========================
# SERIAL
# =========================

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)

# =========================
# DATA STORAGE
# =========================

rtt_values = []
oneway_values = []

# =========================
# REGEX PARSER
# =========================

pattern = r"RTT:\s+(\d+)\s+us\s+\|\s+One-way latency:\s+([\d.]+)\s+ms"

# =========================
# RECORD DATA
# =========================

print(f"\nRecording latency data for {BITRATE_LABEL}...")

start = time.time()

while time.time() - start < MEASURE_TIME:

    line = ser.readline().decode(errors='ignore').strip()

    match = re.search(pattern, line)

    if match:

        rtt = int(match.group(1))
        latency = float(match.group(2))

        rtt_values.append(rtt)
        oneway_values.append(latency)

        print(f"RTT: {rtt} us | Latency: {latency} ms")

ser.close()

print(f"\nCollected {len(rtt_values)} samples")

# =========================
# SAVE CSV
# =========================

with open(csv_filename, mode='w', newline='') as file:

    writer = csv.writer(file)

    writer.writerow([
        "Sample",
        "Bitrate",
        "RTT_us",
        "OneWayLatency_ms"
    ])

    for i in range(len(rtt_values)):

        writer.writerow([
            i + 1,
            BITRATE_LABEL,
            rtt_values[i],
            oneway_values[i]
        ])

print(f"CSV saved as: {csv_filename}")

# =========================
# STATISTICS
# =========================

avg_latency = sum(oneway_values) / len(oneway_values)
min_latency = min(oneway_values)
max_latency = max(oneway_values)

# =========================
# PLOT
# =========================

samples = list(range(1, len(oneway_values) + 1))

plt.figure(figsize=(8,5))

# Latency line
plt.plot(samples, oneway_values, marker='o', label="One-way Latency")

# Average line
plt.axhline(avg_latency, linestyle='--', label=f"Average = {avg_latency:.3f} ms")

# Variation band

"""
plt.fill_between(
    samples,
    [min_latency] * len(samples),
    [max_latency] * len(samples),
    alpha=0.2,
    label="Variation"
)
"""

plt.xlabel("Sample Number")
plt.ylabel("Latency (ms)")
plt.title(f"Latency Test - {BITRATE_LABEL}")
plt.grid(True)
plt.legend()

plt.tight_layout()

# Save plot
plt.savefig(plot_filename, dpi=300)

print(f"Plot saved as: {plot_filename}")

plt.show()