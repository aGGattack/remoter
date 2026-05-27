#include "RadioTrans.h"
#include <SPI.h>
#include <RFM69.h>
#include <RFM69registers.h>

#define RFM69_CS    0
#define RFM69_RST   1
#define RFM69_INT   A4
#define RFM69_DIO2  A3
#define RFM69_DIO3  A5

#define NETWORKID   42
#define NODEID      2
#define TONODEID    1
#define FREQUENCY   RF69_433MHZ
#define LATENCY_PACKET 0x42
#define PACKET_TEST 0x55

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


    //uint16_t bitrate = 32000000 / 9600;

    //radio.writeReg(REG_BITRATEMSB, bitrate >> 8);
    //radio.writeReg(REG_BITRATELSB, bitrate & 0xFF);


    //radio.writeReg(REG_FDEVMSB, 0x00);
    //radio.writeReg(REG_FDEVLSB, 0x52);


    //radio.writeReg(REG_RXBW, 0x55);

    // AFC bandwidth
    //radio.writeReg(REG_AFCBW, 0x8B);



    radio.setHighPower();

    Serial.println("RFM69 init OK");
}

bool sendData(uint8_t x, uint8_t y, uint8_t button, uint8_t *battery, char *robotName, int8_t *RSSI)
{
    uint8_t packet[3];
    packet[0] = x;
    packet[1] = y;
    packet[2] = button;

    if (!radio.sendWithRetry(TONODEID, packet, sizeof(packet), 1, 50))
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


