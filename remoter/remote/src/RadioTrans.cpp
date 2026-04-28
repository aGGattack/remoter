#include "RadioTrans.h"
#include <SPI.h>
#include <RFM69.h>

#define RFM69_CS    A5
#define RFM69_RST   A4
#define RFM69_INT   6
#define RFM69_DIO2  11
#define RFM69_DIO3  12

#define NETWORKID   42
#define NODEID      2
#define TONODEID    1
#define FREQUENCY   RF69_433MHZ

RFM69 radio(RFM69_CS, RFM69_INT);

void transiver_init()
{
    pinMode(RFM69_RST, OUTPUT);
    digitalWrite(RFM69_RST, HIGH);
    delay(50);
    digitalWrite(RFM69_RST, LOW);
    delay(50);

    SPI.begin();

    if (!radio.initialize(FREQUENCY, NODEID, NETWORKID))
    {
        Serial.println("RFM69 init FAILED");
        while (1);
    }

    radio.setHighPower();

    Serial.println("RFM69 init OK");
}

bool sendData(uint8_t x,
              uint8_t y,
              uint8_t button,
              uint8_t *battery,
              char *robotName,
              int8_t *RSSI)
{
    uint8_t packet[3];
    packet[0] = x;
    packet[1] = y;
    packet[2] = button;

    if (!radio.sendWithRetry(TONODEID, packet, sizeof(packet), 5, 20))
    {
        Serial.println("No ACK received");
        return false;
    }

    *battery = radio.DATA[0];

    for (int i = 0; i < 14; i++)
    {
        robotName[i] = (char)radio.DATA[i + 1];

        if (robotName[i] == '\0')
            break;
    }

    robotName[14] = '\0';

    *RSSI = radio.RSSI;

    return true;
}