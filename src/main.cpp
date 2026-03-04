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

    readJoystick(XandY);  // Your function that fills X/Y

    if (sendJoystick(XandY, &masterRSSI, &slaveRSSI)) {
        Display_draw(masterRSSI, slaveRSSI);  // Send to your display
    }

    static bool lastState = HIGH;
    bool currentState = digitalRead(BUTTON_PIN);

    if (lastState == HIGH && currentState == LOW) {
        // Button was just pressed
        sendButton();
    }

    lastState = currentState;

    delay(100);
}