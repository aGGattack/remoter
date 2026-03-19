#ifndef RFM69_H
#define RFM69_H

#include <Arduino.h>

void transiver_init();

bool sendJoystick(uint16_t *XandY, uint8_t button, int16_t *masterRSSI, int16_t *slaveRSSI);

#endif