#!/usr/bin/env python3
"""
Feather M0 Communication Test Script
============================
Usage: python test_feather.py

This script tests serial communication with the Feather M0 (RobotSide).

Setup:
  - Windows: Uses COM8 (change below if different)
  - Linux: Uses /dev/ttyACM1 (change below if different)

Run:
  python test_feather.py

What it does:
  1. Sends "name:TESTBOT,bat:12.34\n" to Feather
  2. Waits for response
  3. Reports what was received

Output examples:
  - "Response: OK" = Feather received and responded
  - "No response" = Feather not receiving data
"""

import serial
import time
import sys

# ==================== CHANGE THESE IF NEEDED ====================
# On Windows (check Device Manager for correct port)
# Common ports: COM3, COM4, COM5, COM6, COM7, COM8, COM10, etc.
WINDOWS_PORT = 'COM8'

# On Linux/Raspberry Pi (check with: ls -l /dev/ttyACM*)
# Common ports: /dev/ttyACM0, /dev/ttyACM1
LINUX_PORT = '/dev/ttyACM1'
# ======================================================

# Platform detection and port selection
if sys.platform.startswith('win'):
    SERIAL_PORT = WINDOWS_PORT
elif sys.platform.startswith('linux'):
    SERIAL_PORT = LINUX_PORT
else:
    SERIAL_PORT = '/dev/ttyUSB0'  # Mac

BAUD_RATE = 115200
TIMEOUT = 2

def test_feather():
    print("=== Feather M0 Communication Test ===")
    print(f"Platform: {sys.platform}")
    print(f"Port: {SERIAL_PORT}")
    print(f"Baud: {BAUD_RATE}")
    print("-" * 40)

    try:
        print("Opening serial port...")
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
        time.sleep(2)  # Wait for Feather to initialize
        print("Port opened!")

        # Send test data - same format as mjoy.cpp
        print("\nSending test data...")
        test_msg = "name:TESTBOT,bat:12.34\n"
        ser.write(test_msg.encode())
        print(f"Sent: {test_msg.strip()}")

        # Read response with multiple attempts
        print("\nReading response...")
        received_any = False
        
        for i in range(3):
            time.sleep(0.5)
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                print(f"Response {i+1}: {data.decode('utf-8', errors='replace').strip()}")
                received_any = True
            else:
                print(f"Attempt {i+1}: No data available")

        if not received_any:
            print("\nNo response received from Feather!")
            print("This means Feather is not responding to the serial data.")

        ser.close()
        print("\n=== Test Complete ===")

    except serial.SerialException as e:
        print(f"\nERROR: {e}")
        print("\nTroubleshooting:")
        print("  - Make sure Feather is connected")
        print("  - Check correct COM port (Windows: COMx, Linux: /dev/ttyACMx)")
        print("  - Close other programs using the port")
        print("  - Try a different USB port")

if __name__ == "__main__":
    test_feather()