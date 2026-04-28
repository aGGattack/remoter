#include <Arduino.h>
#include "OledDis.h"
#include "RadioTrans.h"
#include "Joystick.h"

#define BUTTON_PIN 10
#define VBATPIN A7
#define PWR_CONTROL 5

volatile uint8_t buttonState = 0;

void handleButton() {
  buttonState = !buttonState;
}

void setup() {
  Serial.begin(115200);
  delay(2000);

  pinMode(PWR_CONTROL, OUTPUT);
  digitalWrite(PWR_CONTROL, HIGH);

  pinMode(BUTTON_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), handleButton, FALLING);

  Display_init();

  transiver_init();   

  Serial.println("System ready");
}

void loop() {
  uint8_t x, y;
  int8_t RSSI = 0;
  uint8_t battery = 0;
  char robotName[15] = "none";

  readJoystick(&x, &y);


  // Remote battery mesurements
  float measuredvbat = analogRead(VBATPIN);
  measuredvbat *= 2;
  measuredvbat *= 3.3;
  measuredvbat /= 1024.0;



  sendData(x, y, buttonState, &battery, robotName, &RSSI);
  Display_draw(robotName, measuredvbat, battery, RSSI);

  delay(100);
}