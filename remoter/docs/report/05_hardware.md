# 4. Hardware Architecture

## 4.1 Component Selection

### 4.1.1 Microcontroller: Adafruit Feather M0
- ARM Cortex-M0+ @ 48MHz
- 32KB Flash, 8KB RAM
- Built-in USB, LiPo charging

### 4.1.2 Radio Module: RFM69
- Frequency: 433MHz
- Max power: +20dBm
- SPI interface

### 4.1.3 Display: SSD1306 OLED
- Resolution: 128x32 (or 128x64)
- I2C interface
- Low power consumption

### 4.1.4 Input: Analog Joystick
- Two-axis analog output
- Pushbutton integrated

## 4.2 Pinout Assignments

| Pin | Function | Notes |
|-----|----------|-------|
| A4 | Joystick Y | Analog input |
| A5 | Joystick X | Analog input |
| A2 | Button | Digital input |
| 5 | RFM69 CS | SPI chip select |
| 6 | RFM69 INT | Interrupt |
| 10 | RFM69 RST | Reset |
| SDA | OLED SDA | I2C data |
| SCL | OLED SCL | I2C clock |

## 4.3 Circuit Diagram

[Insert wiring diagram or breadboard layout]

## 4.4 Power Considerations

- USB power or LiPo battery
- Power consumption breakdown:
  - MCU: ~15mA
  - RFM69 (tx): ~130mA
  - OLED: ~10mA
