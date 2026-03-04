#ifndef RFM69_H
#define RFM69_H

#include <Arduino.h>

void transiver_init();
void handleJoystickPacket();
void sendRSSIReply(uint16_t target, int16_t rssi);
void transiver_receive();


#endif