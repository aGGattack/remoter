#include <Arduino.h>
#include "OledDis.h"
#include <Wire.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32

Adafruit_SSD1306 display(
  SCREEN_WIDTH,
  SCREEN_HEIGHT,
  &Wire,     
  -1
);

void Display_init() {
  Wire.begin();
  delay(100);
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED not found");
    while (1);
  }
  Serial.println("OLED found");

  display.clearDisplay();
  display.setRotation(2);
  display.ssd1306_command(SSD1306_DISPLAYON);
  display.ssd1306_command(SSD1306_NORMALDISPLAY);
  display.display();
}

void Display_test() {
  display.clearDisplay();

  display.drawRect(0, 0, 128, 32, SSD1306_WHITE);

  display.drawLine(0, 0, 127, 31, SSD1306_WHITE);

  display.display();
}

void Display_clear() {
  display.clearDisplay();
  display.display();
}

void Display_draw(char *name, float remoteBattery, uint8_t robotBattery, int8_t RSSI) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);

  display.print("Name:");
  display.println(name);

  display.print("R:");
  display.print(remoteBattery, 1);
  display.print("V");

  display.print("B:");
  display.print(robotBattery , 1);
  display.println("V");

  display.print("RSSI:");
  display.println(RSSI);

  display.display();
}
