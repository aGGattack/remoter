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

PACKET_SIZE = 5     # Change for each test
BIT_RATE = 115.2
MEASURE_TIME = 10     # seconds

# =========================
# FILE SETUP
# =========================

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

csv_filename = f"packet_size_{PACKET_SIZE}B_{BIT_RATE}kb{timestamp}.csv"
plot_filename = f"packet_size_{PACKET_SIZE}B_{BIT_RATE}kb{timestamp}.png"

# =========================
# SERIAL
# =========================

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)

# =========================
# DATA STORAGE
# =========================

rtt_values = []
latency_values = []

# =========================
# REGEX PARSER
# =========================

pattern = r"Size:\s+(\d+)\s+bytes\s+\|\s+RTT:\s+(\d+)\s+us\s+\|\s+One-way latency:\s+([\d.]+)\s+ms"

# =========================
# RECORD DATA
# =========================

print(f"\nRecording latency data for packet size = {PACKET_SIZE} bytes")

start = time.time()

while time.time() - start < MEASURE_TIME:

    line = ser.readline().decode(errors='ignore').strip()

    match = re.search(pattern, line)

    if match:

        size = int(match.group(1))
        rtt = int(match.group(2))
        latency = float(match.group(3))

        rtt_values.append(rtt)
        latency_values.append(latency)

        print(f"Size: {size} B | RTT: {rtt} us | Latency: {latency} ms")

ser.close()

print(f"\nCollected {len(latency_values)} samples")

# =========================
# SAVE CSV
# =========================

with open(csv_filename, mode='w', newline='') as file:

    writer = csv.writer(file)

    writer.writerow([
        "Sample",
        "PacketSize_Bytes",
        "RTT_us",
        "OneWayLatency_ms"
    ])

    for i in range(len(latency_values)):

        writer.writerow([
            i + 1,
            PACKET_SIZE,
            rtt_values[i],
            latency_values[i]
        ])

print(f"CSV saved as: {csv_filename}")

# =========================
# STATISTICS
# =========================

avg_latency = sum(latency_values) / len(latency_values)
min_latency = min(latency_values)
max_latency = max(latency_values)

# =========================
# PLOT
# =========================

samples = list(range(1, len(latency_values) + 1))

plt.figure(figsize=(8,5))

# Latency line
plt.plot(samples, latency_values, marker='o', label="One-way Latency")

# Average line
plt.axhline(
    avg_latency,
    linestyle='--',
    label=f"Average = {avg_latency:.3f} ms"
)



plt.xlabel("Sample Number")
plt.ylabel("Latency (ms)")
plt.title(f"Latency vs Time - Packet Size {PACKET_SIZE} Bytes")

plt.grid(True)
plt.legend()

plt.tight_layout()

# Save plot
plt.savefig(plot_filename, dpi=300)

print(f"Plot saved as: {plot_filename}")

plt.show()