#include <Arduino.h>
#include <FastLED.h>

#define HEART_PIN 4
#define LED_PIN 3
#define NUM_LEDS 60
#define LED_TYPE WS2812B
#define COLOR_ORDER GRB

CRGB leds[NUM_LEDS]; // Make array of LEDs

void turnOnLeds(int count);

void setup() {
    // put your setup code here, to run once:
    Serial.begin(9600);
    pinMode(HEART_PIN, OUTPUT);

    FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS);
    FastLED.setBrightness(50); // 0–255

    turnOnLeds(20);
}

void loop() {
    // put your main code here, to run repeatedly:
    if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n');
    if (message.startsWith("DEATH")) {
      String dataStr = message.substring(6); // Get the actual value from the message
      int nrOfDeaths = constrain(dataStr.toInt(), 0, 60);

      turnOnLeds(nrOfDeaths);

      int mappedDeaths = map(nrOfDeaths, 0, 60, 0, 255); // Map to 255

      // Activate heart
      analogWrite(HEART_PIN, mappedDeaths);
    }
  }
}

void turnOnLeds(int count) {
  // Clear all LEDs
  FastLED.clear();

  // Light up 'count' LEDs from index 0
  for (int i = 0; i < count && i < NUM_LEDS; i++) {
    leds[i] = CRGB::Red; // Change color as needed
  }

  FastLED.show();
}