#include <Arduino.h>

constexpr uint8_t BUTTON_COUNT = 3;
const uint8_t buttonPins[BUTTON_COUNT] = {27, 13, 33};
int lastStates[BUTTON_COUNT] = {HIGH, HIGH, HIGH};
int lastbutton = -1;

void setup() {
  Serial.begin(9600);
  for (uint8_t i = 0; i < BUTTON_COUNT; ++i) {
    pinMode(buttonPins[i], INPUT_PULLUP);
  }
}

void loop() {
  for (uint8_t i = 0; i < BUTTON_COUNT; ++i) {
    int currentState = digitalRead(buttonPins[i]);

    if (lastStates[i] == LOW && currentState == HIGH) {
      if (lastbutton != i) {
        char buf[64];
        snprintf(buf, sizeof(buf), "{\"city_location\":%d}", i);
        Serial.println(buf);
        lastbutton = i;
      }
    } 

    lastStates[i] = currentState;
  }
}
