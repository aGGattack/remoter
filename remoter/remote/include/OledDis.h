#pragma once
#include <Arduino.h>

void Display_init();
void Display_test();
void Display_clear();
void Display_draw(char *name, float remoteBattery, uint8_t robotBattery, int8_t RSSI);
