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

  // Force known-good state (NO setContrast)
  display.clearDisplay();
  display.ssd1306_command(SSD1306_DISPLAYON);
  display.ssd1306_command(SSD1306_NORMALDISPLAY);
  display.display();
}

void Display_test() {
  display.clearDisplay();

  // Draw a white border
  display.drawRect(0, 0, 128, 32, SSD1306_WHITE);

  // Draw diagonal line
  display.drawLine(0, 0, 127, 31, SSD1306_WHITE);

  display.display();
}

void Display_clear() {
  display.clearDisplay();
  display.display();
}

void Display_draw(int loRa, int batteri) {
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);

  display.print("master:");
  display.println(loRa);

  display.print("slave:");
  display.println(batteri);

  display.display();
}