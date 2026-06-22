#include <Arduino.h>

constexpr uint8_t BUTTON_COUNT = 12;
constexpr unsigned long DEBOUNCE_MS = 30;
const uint8_t buttonPins[BUTTON_COUNT] = {13, 27, 26, 25, 33, 32, 21,19,18,17,16,4};
int stableButton = -1;
int candidateButton = -1;
unsigned long candidateSince = 0;
int month = 0;

void setup() {
  Serial.begin(9600);
  for (uint8_t i = 0; i < BUTTON_COUNT; ++i) {
    pinMode(buttonPins[i], INPUT_PULLUP);
  }
}

void loop() {
  int observedButton = -1;

  for (uint8_t i = 0; i < BUTTON_COUNT; ++i) {
    int currentState = digitalRead(buttonPins[i]);

    if (currentState == LOW) {
      observedButton = i;
      break;
    } 
  }

  if (observedButton != candidateButton) {
    candidateButton = observedButton;
    candidateSince = millis();
  }

  if (candidateButton != stableButton && (millis() - candidateSince) >= DEBOUNCE_MS) {
    stableButton = candidateButton;
    month = stableButton + 1;
    char buf[64];
    snprintf(buf, sizeof(buf), "{\"month\":%d}", month);
    Serial.println(buf);
  }
}
