#include <Arduino.h>
#include <FastLED.h>

#define HEART_PIN 4
#define LED_PIN 3
#define NUM_LEDS 60

CRGB leds[NUM_LEDS]; // Make array of LEDs

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(heartPin, OUTPUT);
  pinMode(LEDPin, OUTPUT);

  FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS);
  FastLED.setBrightness(50); // 0–255
}

void loop() {
    turnOnLeds(20);
    // put your main code here, to run repeatedly:
    if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n');
    if (message.startsWith("DEATH")) {
      String dataStr = message.substring(12); // Get the actual value from the message
      int nrOfDeaths = dataStr.toInt();
      nrOfDeaths = constrain(nrOfDeaths, 0, 60); // Clamp

      turnOnLeds(nrOfDeaths);

      int mappedDeaths = int(map(nrOfDeaths, 0, 60, 0, 255)); // Map to 255
      mappedDeaths = constrain(mappedDeaths, 0, 255); // Clamp

      // Acitvate heart
      analogWrite(HEART_PIN, mappedDeaths);
      Serial.println("success");
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