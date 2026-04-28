#include <Arduino.h>

#define Xin = A5
#define Yin = A4

void readJoystick(uint8_t *x, uint8_t *y) {
    *x = analogRead(A3) >> 2;
    *y = analogRead(A2) >> 2;
}
