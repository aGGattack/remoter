#ifndef RADIO_PROTOCOL_H
#define RADIO_PROTOCOL_H

#include <Arduino.h>
#include <stdint.h>

#define NETWORKID  42
#define FREQUENCY  RF69_433MHZ

enum PacketType : uint8_t {
    PKT_JOYSTICK = 1,
    PKT_RSSI     = 2,
    PKT_BUTTON   = 3
};

enum NodeID : uint8_t {
    NODE_REMOTE = 2,
    NODE_ROBOT  = 1
};

#endif
