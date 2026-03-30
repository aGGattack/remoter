#include <Arduino.h>
#include <SPI.h>
#include <RFM69.h>
#include "RemoteTransiver.h"

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);

  transiver_init();
}

void loop() {
  transiver_receive();
}
