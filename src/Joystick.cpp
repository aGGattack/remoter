#include <Arduino.h>

#define Xin = A5
#define Yin = A4

void readJoystick(uint16_t *XandY) {
    XandY[0] = analogRead(A5);
    XandY[1] = analogRead(A4);
}