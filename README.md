# Bachelor Project - Remote Controller System

This repository contains all materials for the Bachelor project, including firmware code and PCB design files.

---

## Project Structure

```
bachelor/
├── remoter/              # Firmware code
│   ├── remote/          # Handheld remote controller firmware
│   ├── robot/           # Robot receiver firmware
│   ├── lib/             # Shared libraries
│   ├── docs/            # Project documentation
│   └── platformio.ini   # PlatformIO configuration
│
├── pcb/                 # PCB design files (KiCad)
│   ├── PCB remote.kicad_pro     # Project file
│   ├── PCB remote.kicad_pcb     # PCB layout
│   ├── PCB remote.kicad_sch     # Schematic
│   ├── PCB remote.kicad_dru    # Design rules
│   ├── Remote-footprints.pretty # Custom footprints
│   └── fp-lib-table     # Footprint library table
│
├── Bachelor_Contract.pdf
└── project_plan/        # Project plan documents
```

---

## Hardware Components

| Component | Description |
|-----------|-------------|
| **MCU** | Adafruit Feather M0 (ARM Cortex-M0+) |
| **Radio** | RFM69 433MHz LoRa transceiver |
| **Display** | SSD1306 128x32 OLED |
| **Input** | Analog dual-axis joystick |

---

## Firmware Development

### Prerequisites

- [PlatformIO](https://platformio.org/) installed

### Build & Upload

```bash
cd remoter

# Build and upload to remote
pio run -e remote --target upload

# Build and upload to robot
pio run -e robot --target upload
```

---

## PCB Development

### Prerequisites

- [KiCad](https://www.kicad.org/) installed

### Opening the PCB Project

1. Open KiCad
2. Open `pcb/PCB remote.kicad_pro`

---

## License

MIT License
