#include <SPI.h>
#include <RFM69.h>
#include "RemoteTransiver.h"

#define RFM69_CS   A5
#define RFM69_INT  6
#define RFM69_RST  A4

#define NETWORKID  42
#define NODEID     1
#define TONODEID   2
#define FREQUENCY  RF69_433MHZ

#define BATTERY_PLACEHOLDER 100

RFM69 radio(RFM69_CS, RFM69_INT);

void transiver_init() {

    pinMode(RFM69_RST, OUTPUT);
    digitalWrite(RFM69_RST, HIGH);
    delay(100);
    digitalWrite(RFM69_RST, LOW);
    delay(100);

    if (!radio.initialize(FREQUENCY, NODEID, NETWORKID)) {
        Serial.println("RFM69 init FAILED");
        while (1);
    }
    radio.setHighPower();

    Serial.println("RFM69 init OK");
}

void handleDataPacket(uint8_t x, uint8_t y, uint8_t button) {
    static int16_t lastRSSI = 0;

    lastRSSI = radio.RSSI;

    Serial.print("x:");
    Serial.print(x);
    Serial.print(", y:");
    Serial.print(y);
    Serial.print(", btn:");
    Serial.print(button);
    Serial.print(", rssi:");
    Serial.println(lastRSSI);
}


void transiver_receive() {

    if (radio.receiveDone()) {

        if (radio.ACKRequested()) {
            uint8_t ackPayload[2];
            ackPayload[0] = (uint8_t)radio.RSSI;
            ackPayload[1] = BATTERY_PLACEHOLDER;
            radio.sendACK(ackPayload, sizeof(ackPayload));
        }

        
            uint8_t x = radio.DATA[0];
            uint8_t y = radio.DATA[1];
            uint8_t button = radio.DATA[2];

            handleDataPacket(x, y, button);
        
    }
}
