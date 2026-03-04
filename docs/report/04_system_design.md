# 3. System Design

## 3.1 High-Level Architecture

```
[Insert architecture diagram here]

┌─────────────┐     Wireless      ┌─────────────┐
│   Remote    │ ◄──────────────► │  Receiver   │
│  (Feather   │     RFM69        │  (Feather   │
│     M0)     │                  │     M0)     │
└─────────────┘                  └─────────────┘
     │                              │
  Joystick                      Actuation
  Button                        Output
  OLED                          Status LED
```

## 3.2 Requirements Analysis

### 3.2.1 Functional Requirements
- RF1: Read analog joystick X/Y position
- RF2: Transmit joystick data wirelessly
- RF3: Display link quality (RSSI)
- RF4: Detect and transmit button presses
- RF5: Receive acknowledgment from receiver

### 3.2.2 Non-Functional Requirements
- NFR1: Range of at least [X] meters
- NFR2: Latency under [X] ms
- NFR3: Reliable packet delivery
- NFR4: Low power consumption

## 3.3 Design Decisions

### 3.3.1 Frequency Selection
- 433MHz chosen for [reasons]

### 3.3.2 Communication Protocol
- Custom packet format
- ACK-based reliability

## 3.4 Tradeoffs

| Decision | Pros | Cons |
|----------|------|------|
| [Decision 1] | [Pro] | [Con] |
