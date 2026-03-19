#include <SPI.h>
#include <RFM69.h>
#include "RemoteTransiver.h"
#include <RadioProtocol.h>

#define RFM69_CS   5
#define RFM69_INT  6
#define RFM69_RST  10

#define NODEID     NODE_ROBOT
#define TONODEID   NODE_REMOTE



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

void handleJoystickPacket(uint8_t *data, uint8_t len) {
    if (len < 5) return;

    uint16_t x, y;
    uint8_t button;

    memcpy(&x, &data[0], sizeof(uint16_t));
    memcpy(&y, &data[2], sizeof(uint16_t));
    button = data[4];

    static int16_t lastRSSI = 0;

    lastRSSI = radio.RSSI;

    Serial.print("joy, ");
    Serial.print(x);
    Serial.print(", ");
    Serial.print(y);
    Serial.print(", ");
    Serial.print(lastRSSI);
    Serial.print(", ");
    Serial.println(button);
}


void sendRSSIReply(uint16_t target, int16_t rssi) {
    uint8_t reply[2];
    memcpy(&reply[0], &rssi, sizeof(int16_t));

    radio.send(target, reply, sizeof(reply));
    radio.receiveDone(); 
}

void transiver_receive() {

    static int16_t  lastRSSI = 0;
    static bool havePendingRSSIReply = false;
    static unsigned long replyAt = 0;

    if (radio.receiveDone()) {

        if (radio.ACKRequested()) {
            radio.sendACK();  
        }

        handleJoystickPacket(radio.DATA, radio.DATALEN);
        havePendingRSSIReply = true;
        lastRSSI = radio.RSSI;
    }

    if (havePendingRSSIReply && millis() >= replyAt) {
        sendRSSIReply(TONODEID, lastRSSI);
        havePendingRSSIReply = false;
    }
}
