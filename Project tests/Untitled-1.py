#!/usr/bin/env python3
"""
Feather M0 Communication Test Script (Windows)
Run with:
    python test_feather.py
"""

import serial
import time

# CHANGE THIS if your Feather uses another COM port
SERIAL_PORT = "COM8"
BAUD_RATE = 115200
TIMEOUT = 2


def test_feather():
    print("=== Feather M0 Communication Test ===")
    print("Port:", SERIAL_PORT)
    print("Baud:", BAUD_RATE)
    print("-" * 40)

    try:
        # Open serial port
        print("Opening serial port...")
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)

        # Feather often resets when serial opens
        time.sleep(2)

        print("Waiting for Feather to boot...")
        start = time.time()
        while time.time() - start < 5:
            if ser.in_waiting > 0:
                line = ser.readline().decode("utf-8", errors="replace").strip()
                print("Boot message:", line)
                if "init OK" in line:
                    print("Feather is ready!")
                    break
            time.sleep(0.1)

        # NOW send your message
        time.sleep(0.1)
        ser.reset_input_buffer()
        test_msg = "name:TESTBOT,bat:12.34\n"
        print("Sending:", test_msg.strip())
        ser.write(test_msg.encode("utf-8"))
        ser.flush()

        # Wait for reply
        print("\nWaiting for response...\n")

        received = False

        for i in range(5):
            time.sleep(0.5)

            while ser.in_waiting > 0:
                line = ser.readline().decode("utf-8", errors="replace").strip()
                if line:
                    print("Received:", line)
                    received = True

        if not received:
            print("No response received.")

        ser.close()
        print("\n=== Done ===")

    except Exception as e:
        print("ERROR:", e)


# FIXED THIS LINE:
if __name__ == "__main__":
    test_feather()