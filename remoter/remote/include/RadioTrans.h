#ifndef RFM69_H
#define RFM69_H

#include <Arduino.h>

void transiver_init();

bool sendData(uint8_t x,
              uint8_t y,
              uint8_t button,
              uint8_t *battery,
              char *robotName,
              int8_t *RSSI);
#endif
