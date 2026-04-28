#include <SPI.h>
#include <RFM69.h>
#include "RemoteTransiver.h"

#define RFM69_CS   A5
#define RFM69_INT  6
#define RFM69_RST  A4
#define ESTOP      A3
#define LED_PIN    13

#define NETWORKID  42
#define NODEID     1
#define TONODEID   2
#define FREQUENCY  RF69_433MHZ

RFM69 radio(RFM69_CS, RFM69_INT);

float batteryVoltage = 0;       
char robotName[16] = "none/con";     
bool piDataReceived = false;     


void transiver_init()
{
    pinMode(LED_PIN, OUTPUT);
    pinMode(RFM69_RST, OUTPUT);
    digitalWrite(RFM69_RST, HIGH);
    delay(100);
    digitalWrite(RFM69_RST, LOW);
    delay(100);

    pinMode(ESTOP, OUTPUT);

    if (!radio.initialize(FREQUENCY, NODEID, NETWORKID))
    {
        Serial.println("RFM69 init FAILED");
        while (1);
    }

    radio.setHighPower();

    Serial.println("RFM69 init OK");
}

void readPiSerial()
{
    static char line[64];
    static uint8_t idx = 0;

    while (Serial.available())
    {
        char c = Serial.read();
        if (c == '\r') continue;

        if (c == '\n')
        {
            line[idx] = '\0';
            idx = 0;

            // Find "name:" 
            char* namePtr = strstr(line, "name:");
            char* batPtr  = strstr(line, ",bat:");

            if (namePtr && batPtr)
            {
                namePtr += 5; // skip "name:"

                // Copy name up to the comma
                uint8_t i = 0;
                while (namePtr[i] != ',' && namePtr[i] != '\0' && i < 15)
                {
                    robotName[i] = namePtr[i];
                    i++;
                }
                robotName[i] = '\0';

                // Parse float manually
                batPtr += 5; // skip ",bat:"
                batteryVoltage = atof(batPtr);
                piDataReceived = true;


            }

        }
        else
        {
            if (idx < sizeof(line) - 1)
                line[idx++] = c;
            else
                idx = 0;
        }
    }
}


void handleDataPacket(uint8_t x, uint8_t y, uint8_t button)
{

    Serial.print("x:");
    Serial.print(x);
    Serial.print(", y:");
    Serial.print(y);
    Serial.print(", btn:");
    Serial.println(button);

    if (button == 1)
        digitalWrite(ESTOP, HIGH);
    else
        digitalWrite(ESTOP, LOW);
}


void transiver_receive()
{

    readPiSerial();

    if (radio.receiveDone())
    {
        if (radio.ACKRequested())
        {

            uint8_t ackPayload[16];

            // Battery voltage, e.g. 24.3V -> 243
            ackPayload[0] = (uint8_t)(batteryVoltage * 10.0);

            // Copy robot name into remaining bytes
            uint8_t i = 0;
            for (; i < 14 && robotName[i] != '\0'; i++)
            {
                ackPayload[i + 1] = robotName[i];
            }

            // Zero-fill rest
            for (; i < 14; i++)
            {
                ackPayload[i + 1] = 0;
            }

            radio.sendACK(ackPayload, 15);
        }

        uint8_t x      = radio.DATA[0];
        uint8_t y      = radio.DATA[1];
        uint8_t button = radio.DATA[2];

        handleDataPacket(x, y, button);
    }
}


void printRSSI()
{
    if (radio.receiveDone())
    {
        Serial.print("RSSI: ");
        Serial.println(radio.RSSI);
    }
}