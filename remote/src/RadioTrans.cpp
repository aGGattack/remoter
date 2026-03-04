#include "RadioTrans.h"
#include <SPI.h>
#include <RFM69.h>
#include <RadioProtocol.h>


#define RFM69_CS   5
#define RFM69_INT  6
#define RFM69_RST  10

#define NODEID     NODE_REMOTE
#define TONODEID   NODE_ROBOT


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
    //radio.encrypt("sampleEncryptKey"); 

    Serial.println("RFM69 init OK");
}



bool sendJoystick(uint16_t *XandY, int16_t *masterRSSI, int16_t *slaveRSSI) {
    uint8_t packet[1 + 4];  

    packet[0] = PKT_JOYSTICK;               
    memcpy(&packet[1], XandY, sizeof(uint16_t) * 2);


    if (!radio.sendWithRetry(TONODEID, packet, sizeof(packet), 5, 20)) {
        Serial.println("No ACK received");
        return false;
    }


    unsigned long start = millis();
    while (millis() - start < 80) {
        if (radio.receiveDone()) {
            *masterRSSI = radio.RSSI;

            if (radio.DATA[0] == PKT_RSSI && radio.DATALEN == 3) {
                memcpy(slaveRSSI, &radio.DATA[1], sizeof(int16_t));
                return true;
            }
        }
    }

    Serial.println("Timeout waiting for reply");
    return false;
}

bool sendButton() {
    uint8_t packet[1];  

    packet[0] = PKT_BUTTON;               

    if (!radio.sendWithRetry(TONODEID, packet, sizeof(packet), 5, 20)) {
        Serial.println("No ACK received");
        return false;
    }

    Serial.println("Timeout waiting for reply");
    return false;
}