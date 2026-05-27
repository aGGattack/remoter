#include <Arduino.h>


void readJoystick(uint8_t *x, uint8_t *y) {
    *x = -analogRead(A0) >> 2;
    *y = -analogRead(A1) >> 2;
}
