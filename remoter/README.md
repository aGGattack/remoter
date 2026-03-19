# Remoter - Wireless Remote Controller System

A wireless remote controller system built with Arduino-compatible hardware. Control a robot remotely using a joystick with real-time feedback via OLED display and radio communication.

---

## Project Structure

```
remoter/
├── remote/                 # Handheld remote controller
│   ├── src/
│   │   ├── main.cpp        # Main loop
│   │   ├── Joystick.cpp    # Joystick input handling
│   │   ├── RadioTrans.cpp # RFM69 wireless transmission
│   │   └── OledDis.cpp    # OLED display interface
│   └── include/            # Header files
│
├── robot/                  # Robot receiver
│   ├── src/
│   │   ├── main.cpp       # Main loop
│   │   └── RemoteTransiver.cpp  # Radio receive handler
│   └── include/           # Header files
│
├── lib/
│   └── common/            # Shared libraries
│       └── RadioProtocol.h # Protocol definitions
│
├── docs/                  # Project documentation
│   └── report/            # Report markdown files
│
└── platformio.ini         # PlatformIO workspace config
```

---

## Hardware

| Component | Description |
|-----------|-------------|
| **MCU** | Adafruit Feather M0 (ARM Cortex-M0+) |
| **Radio** | RFM69 433MHz LoRa transceiver |
| **Display** | SSD1306 128x32 OLED |
| **Input** | Analog dual-axis joystick |

---

## Quick Start

### Prerequisites

- [PlatformIO](https://platformio.org/) installed
- USB cable for programming

### Build & Upload

```bash
# Build remote
pio run -e remote

# Upload to remote
pio run -e remote --target upload

# Build robot
pio run -e robot

# Upload to robot
pio run -e robot --target upload
```

### Monitor Output

```bash
# Monitor remote serial
pio device monitor -b 115200 --port <serial_port>

# Monitor robot serial
pio device monitor -b 115200 --port <serial_port>
```

---

## Communication Protocol

| Packet Type | ID | Data |
|-------------|----|------|
| JOYSTICK | 1 | X (uint16) + Y (uint16) |
| RSSI | 2 | RSSI value (int16) |
| BUTTON | 3 | (none) |

- **Network ID**: 42
- **Frequency**: 433MHz
- **Remote Node ID**: 2
- **Robot Node ID**: 1

---

## Features

- [x] Analog joystick input (10-bit ADC)
- [x] Wireless transmission via RFM69
- [x] OLED display for link quality (RSSI)
- [x] Button press detection
- [x] Acknowledgment-based reliability
- [x] Bidirectional RSSI reporting

---

## Pin Configuration

### Remote

| Pin | Function |
|-----|----------|
| A4 | Joystick Y-axis |
| A5 | Joystick X-axis |
| A2 | Button input |
| 5 | RFM69 CS |
| 6 | RFM69 INT |
| 10 | RFM69 RST |
| SDA/SCL | OLED I2C |

### Robot

| Pin | Function |
|-----|----------|
| 5 | RFM69 CS |
| 6 | RFM69 INT |
| 10 | RFM69 RST |

---

## Dependencies

- [LowPowerLab RFM69](https://github.com/LowPowerLab/RFM69)
- [Adafruit SSD1306](https://github.com/adafruit/Adafruit_SSD1306)
- [Adafruit GFX](https://github.com/adafruit/Adafruit-GFX-Library)

---

## License

MIT License
