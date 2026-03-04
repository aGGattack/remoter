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

void handleJoystickPacket() {
    uint16_t x, y;

    memcpy(&x, &radio.DATA[1], sizeof(uint16_t));
    memcpy(&y, &radio.DATA[3], sizeof(uint16_t));

    static int16_t  lastRSSI   = 0;

    lastRSSI   = radio.RSSI;

    Serial.print("joy, ");
    Serial.print(x);
    Serial.print(", ");
    Serial.print(y);
    Serial.print(", ");
    Serial.println(lastRSSI);

    
}


void sendRSSIReply(uint16_t target, int16_t rssi) {
    uint8_t reply[3];
    reply[0] = PKT_RSSI;
    memcpy(&reply[1], &rssi, sizeof(int16_t));

    radio.send(target, reply, sizeof(reply));
    radio.receiveDone(); 
}

void transiver_receive() {

    static int16_t  lastRSSI = 0;
    static bool havePendingRSSIReply = false;
    static unsigned long replyAt = 0;
    static bool buttonbool = false;

    if (radio.receiveDone()) {

        if (radio.ACKRequested()) {
            radio.sendACK();  
        }

        uint8_t cmd = radio.DATA[0];

        switch (cmd) {

            case PKT_JOYSTICK: {
                handleJoystickPacket();
                havePendingRSSIReply = true;
                //replyAt = millis() + 12; 
                lastRSSI   = radio.RSSI;
                break;
            }

            case PKT_BUTTON:
                if (buttonbool){
                    buttonbool = false;
                    Serial.println("bot, F");
                }
                else{
                    buttonbool = true;
                    Serial.println("bot, T");
                }
                break;

            default:
                Serial.print("Unknown packet type: ");
                Serial.println(cmd);
                break;
        }
    }

    if (havePendingRSSIReply && millis() >= replyAt) {
        sendRSSIReply(TONODEID, lastRSSI);
        havePendingRSSIReply = false;
    }
}
