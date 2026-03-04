# 5. Software Architecture

## 5.1 Module Overview

The software is organized into three main modules:

```
┌─────────────────────────────────────┐
│            main.cpp                 │
│    (Main loop, coordination)        │
└──────────┬──────────┬───────────────┘
           │          │
    ┌──────▼──┐ ┌─────▼─────┐
    │Joystick │ │RadioTrans │
    │ Module  │ │  Module   │
    └──────┬──┘ └─────┬─────┘
           │          │
    ┌──────▼──────────▼─────┐
    │      OledDis          │
    │      Module           │
    └───────────────────────┘
```

## 5.2 Joystick Module

### 5.2.1 Functions
- `readJoystick(uint16_t *XandY)` - Reads X/Y analog values

### 5.2.2 Implementation Details
- Uses analogRead() on A4 (Y) and A5 (X)
- Returns 10-bit ADC values (0-1023)

## 5.3 Radio Module

### 5.3.1 Packet Format

```
┌──────────┬──────────┬──────────┐
│  Type    │   Data   │   CRC    │
│ (1 byte) │ (N bytes)│(optional)│
└──────────┴──────────┴──────────┘
```

### 5.3.2 Packet Types
| Type ID | Name | Description |
|---------|------|-------------|
| 1 | PKT_JOYSTICK | Joystick X/Y data |
| 2 | PKT_RSSI | RSSI response |
| 3 | PKT_BUTTON | Button press |

### 5.3.3 Functions
- `transiver_init()` - Initialize RFM69
- `sendJoystick()` - Send and wait for ACK
- `sendButton()` - Send button press

## 5.4 Display Module

### 5.4.1 Functions
- `Display_init()` - Initialize OLED
- `Display_draw()` - Show RSSI values

### 5.4.2 Screen Layout

```
┌────────────────────────┐
│ master: -65 dBm        │
│ slave:  -72 dBm        │
└────────────────────────┘
```

## 5.5 Main Loop State Machine

```
START
  │
  ▼
┌──────────────────┐
│ Read Joystick    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Send via Radio  │── No ACK ──► [Retry or skip]
└────────┬─────────┘
         │ ACK received
         ▼
┌──────────────────┐
│ Update Display   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Check Button     │
└────────┬─────────┘
         │
         ▼
       DELAY
         │
         ▼
      LOOP
```
