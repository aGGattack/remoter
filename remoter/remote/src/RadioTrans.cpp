#include "RadioTrans.h"
#include <SPI.h>
#include <RFM69.h>


#define RFM69_CS   5
#define RFM69_INT  6
#define RFM69_RST  10

#define NETWORKID  42
#define NODEID     2
#define TONODEID   1
#define FREQUENCY  RF69_433MHZ

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



bool sendData(uint8_t x, uint8_t y, uint8_t button, int16_t *masterRSSI, int8_t *slaveRSSI, uint8_t *battery) {
    uint8_t packet[3];
    packet[0] = x;
    packet[1] = y;
    packet[2] = button;

    if (!radio.sendWithRetry(TONODEID, packet, sizeof(packet), 5, 20)) {
        Serial.println("No ACK received");
        return false;
    }

    *masterRSSI = radio.RSSI;
    *slaveRSSI = (int8_t)radio.DATA[0];
    *battery = radio.DATA[1];

    return true;
}
