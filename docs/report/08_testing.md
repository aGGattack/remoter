# 7. Testing & Results

## 7.1 Test Methodology

### 7.1.1 Unit Testing
- Testing each module independently
- Joystick: Verify ADC readings
- Radio: Loopback test (if possible)
- Display: Basic render test

### 7.1.2 Integration Testing
- End-to-end communication test
- Range testing
- Latency measurement

### 7.1.3 Test Equipment
- [List equipment used]
- Serial monitor for debugging
- Power supply measurements

## 7.2 Test Results

### 7.2.1 Joystick Readings
| Position | X Value | Y Value |
|----------|---------|---------|
| Center | ~512 | ~512 |
| Left | ~0 | ~512 |
| Right | ~1023 | ~512 |
| Up | ~512 | ~0 |
| Down | ~512 | ~1023 |

### 7.2.2 Range Test Results
[Add your actual test data]

| Distance | Packets Sent | Packets Received | Success Rate |
|----------|--------------|-------------------|--------------|
| 10m | [X] | [X] | [X]% |
| 50m | [X] | [X] | [X]% |
| 100m | [X] | [X] | [X]% |

### 7.2.3 Latency Measurements
- Average round-trip time: [X] ms
- Standard deviation: [X] ms

### 7.2.4 RSSI Values
[Add RSSI at various distances]

## 7.3 Demo

[Describe or reference demo video/screenshots]

## 7.4 Summary

- [Key finding 1]
- [Key finding 2]
- [Performance meets/does not meet requirements]
