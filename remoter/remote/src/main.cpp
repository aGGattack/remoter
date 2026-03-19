#include <Arduino.h>
#include "OledDis.h"
#include "RadioTrans.h"
#include "Joystick.h"


#define BUTTON_PIN A2


void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10); 

  pinMode(BUTTON_PIN, INPUT_PULLUP);

  transiver_init();
  Display_init();

}

void loop() {
  uint16_t XandY[2];
    int16_t masterRSSI = 0;
    int16_t slaveRSSI  = 0;

    readJoystick(XandY);

    bool currentState = digitalRead(BUTTON_PIN);
    static bool lastState = HIGH;
    uint8_t buttonPressed = (lastState == HIGH && currentState == LOW) ? 1 : 0;

    if (sendJoystick(XandY, buttonPressed, &masterRSSI, &slaveRSSI)) {
        Display_draw(masterRSSI, slaveRSSI);
    }

    lastState = currentState;

    delay(100);
}