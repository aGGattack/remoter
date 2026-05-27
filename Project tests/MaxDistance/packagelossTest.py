import serial
import time
import matplotlib.pyplot as plt
import csv
from datetime import datetime

SERIAL_PORT = "COM8"
BAUD_RATE = 115200

# Test distances
DISTANCES = list([20, 40, 50, 70])  # 0,10,20,...80 meters

EXPECTED_PACKETS = 100

# Timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

csv_filename = f"packet_loss_test_{timestamp}.csv"
plot_filename = f"packet_loss_plot_{timestamp}.png"

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)

results = {}

# =========================
# Test Loop
# =========================

for dist in DISTANCES:

    print(f"\nMove robot to {dist} meters")
    input("Press ENTER when ready...")

    print("Waiting for packets...")

    received_packets = set()

    start_time = time.time()

    # Wait until transmission finishes
    while time.time() - start_time < 10:

        line = ser.readline().decode(errors='ignore').strip()

        if "Received packet:" in line:
            try:
                packet_num = int(line.split(":")[1])

                received_packets.add(packet_num)

                print(f"{dist}m -> Packet {packet_num}")

            except:
                pass

    received_count = len(received_packets)
    lost_count = EXPECTED_PACKETS - received_count
    loss_percent = (lost_count / EXPECTED_PACKETS) * 100

    results[dist] = {
        "received": received_count,
        "lost": lost_count,
        "loss_percent": loss_percent
    }

    print("\n========== RESULT ==========")
    print(f"Distance: {dist} m")
    print(f"Received: {received_count}")
    print(f"Lost: {lost_count}")
    print(f"Packet Loss: {loss_percent:.1f}%")
    print("============================")

ser.close()

# =========================
# Save CSV
# =========================

with open(csv_filename, mode='w', newline='') as file:

    writer = csv.writer(file)

    writer.writerow([
        "Distance_m",
        "Received_Packets",
        "Lost_Packets",
        "Packet_Loss_Percent"
    ])

    for dist in DISTANCES:

        writer.writerow([
            dist,
            results[dist]["received"],
            results[dist]["lost"],
            results[dist]["loss_percent"]
        ])

print(f"\nCSV saved as: {csv_filename}")

# =========================
# Plotting
# =========================

distances = []
losses = []

for dist in DISTANCES:
    distances.append(dist)
    losses.append(results[dist]["loss_percent"])

plt.figure(figsize=(8, 5))

plt.plot(distances, losses, marker='o')

plt.xlabel("Distance (m)")
plt.ylabel("Packet Loss (%)")
plt.title("Packet Loss vs Distance")

plt.grid(True)

plt.tight_layout()

plt.savefig(plot_filename, dpi=300)

print(f"Plot saved as: {plot_filename}")

plt.show()