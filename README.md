# Bachelor Project - Wireless Remote Controller System

Remote control system for a robot, built around an **Adafruit Feather M0** with an **RFM69 433 MHz** radio, consisting of a handheld remote controller and a robot-side receiver.

---

## Repository Structure

```
bachelor/
├── remoter/                         # Firmware source code
│   ├── Remote/                      # Handheld remote controller
│   │   ├── src/main.cpp             # Main loop, 10Hz control rate
│   │   ├── src/RadioTrans.cpp       # RFM69 radio (TX, ACK)
│   │   ├── src/Joystick.cpp         # Analog joystick driver
│   │   ├── src/OledDis.cpp          # SSD1306 OLED display driver
│   │   ├── include/                 # Headers
│   │   └── platformio.ini           # PlatformIO config
│   │
│   └── RobotSide/                   # Robot-mounted receiver
│       ├── src/main.cpp             # Main loop, serial bridge
│       ├── src/RemoteTransiver.cpp  # RFM69 radio (RX, ACK) + serial
│       ├── include/                 # Headers
│       └── platformio.ini           # PlatformIO config
│
├── UniRemote/                       # Remote controller PCB (KiCad)
│   ├── PCB remote.kicad_sch         # Schematic
│   ├── PCB remote.kicad_pcb         # PCB layout
│   ├── PCB remote.kicad_pro         # Project file
│   └── Remote-footprints.pretty/    # Custom footprints
│
├── UniRobot/                        # Robot receiver PCB (KiCad)
│   ├── UniRobot.kicad_sch           # Schematic
│   ├── UniRobot.kicad_pcb           # PCB layout
│   ├── UniRobot.kicad_pro           # Project file
│   └── Remote-footprints.pretty/    # Custom footprints
│
├── Project tests/                   # RFM69 performance characterization
│   ├── BitRateLatencyTest.py        # Latency vs bitrate (1.2-250 kbps)
│   ├── PackageSizeLatencyTest.py    # Latency vs packet size (5-64 B)
│   ├── MaxDistance/                 # Packet loss vs distance
│   ├── RSSI_Antenna_test/           # RSSI vs distance + antenna length
│   ├── OrrientationTest/            # RSSI vs antenna orientation
│   └── latency_Bitrate_test/        # Plotting scripts
│
├── project_plan/                    # Project plan (LaTeX, diagrams)
├── Bachelor_Contract.pdf
├── appendix_code_listings.tex       # Full source listings for report
├── UniRemote v1.zip, v1.5.zip, ...  # PCB version archives
└── UniRobot v1.zip, v1.5.zip, ...
```

---

## Hardware

| Component | Description |
|-----------|-------------|
| **MCU** | Adafruit Feather M0 (ATSAMD21G18A, ARM Cortex-M0+) |
| **Radio** | RFM69HCW 433 MHz transceiver |
| **Display** | SSD1306 128x32 OLED, I2C |
| **Input** | Analog dual-axis joystick + push button (E-stop) |
| **Battery** | LiPo with voltage monitor via A7 |

---

## Firmware

### How It Works

- **Remote** reads joystick X/Y (8-bit), button state, and battery voltage. Transmits 3-byte packets every 100 ms to the robot (NodeID=1). Receives ACK containing robot battery voltage and robot name. Displays RSSI, local & remote battery, and robot name on the OLED.
- **RobotSide** receives joystick packets and forwards them over serial to a Raspberry Pi as `x:<val>, y:<val>, btn:<val>`. Sends ACKs with robot battery and name (parsed from Pi serial input `name:<n>,bat:<v>`). Drives an E-stop output pin.

### Prerequisites

- [PlatformIO](https://platformio.org/)

### Build & Upload

```bash
# Remote controller
cd remoter/Remote
pio run -e adafruit_feather_m0 --target upload

# Robot-side receiver
cd remoter/RobotSide
pio run -e adafruit_feather_m0 --target upload
```

### Serial Monitor

```bash
pio device monitor --baud 115200
```

---

## PCB Design

Both PCBs designed in **KiCad**. To open:

```
# Remote
UniRemote/PCB remote.kicad_pro

# Robot
UniRobot/UniRobot.kicad_pro
```

---

## RF Performance Tests

Python scripts in `Project tests/` characterize the RFM69 link:

| Test | What it measures |
|------|-----------------|
| `BitRateLatencyTest.py` | One-way latency from 1.2 to 250 kbps |
| `PackageSizeLatencyTest.py` | Latency vs payload size at multiple bitrates |
| `MaxDistance/packagelossTest.py` | Packet loss ratio from 20 to 70 m |
| `RSSI_Antenna_test/RSSItest.py` | RSSI vs distance for a given antenna |
| `OrrientationTest/OrrientationsTest.py` | RSSI vs antenna orientation |
| Various `plot_*.py` | Generate plots from collected CSV data |
