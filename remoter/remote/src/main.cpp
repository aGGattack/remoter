#include <Arduino.h>
#include "OledDis.h"
#include "RadioTrans.h"
#include "Joystick.h"


#define BUTTON_PIN A2
#define VBATPIN A7



volatile uint8_t buttonState = 0;


void handleButton() {
    buttonState = !buttonState;
}


void setup() {
  Serial.begin(115200);

  pinMode(BUTTON_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), handleButton, FALLING);

  transiver_init();
  Display_init();


}

void loop() {
  uint8_t x, y;
  int16_t masterRSSI = 0;
  int8_t slaveRSSI = 0;
  uint8_t robotBattery = 0;
  float remoteBattery = 0;

  readJoystick(&x, &y);

  float measuredvbat = analogRead(VBATPIN);
  measuredvbat *= 2;
  measuredvbat *= 3.3;
  measuredvbat /= 1024;
  remoteBattery = measuredvbat;

  if (sendData(x, y, buttonState, &masterRSSI, &slaveRSSI, &robotBattery)) {
    Display_draw(slaveRSSI, remoteBattery, robotBattery);
  }

  delay(100);
}
