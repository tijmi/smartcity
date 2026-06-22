#include <Arduino.h>

#define heartPin 4
#define LEDPin 3


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(heartPin, OUTPUT);
  pinMode(LEDPin, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
    if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n');
    if (message.startsWith("DEATH")) {
      String speedStr = message.substring(12); // Get the actual speed value from the message
      int speed = speedStr.toInt();

      int mappedSpeed = int(map(speed, 0, 5, 0, 255)); // Map to 255
      mappedSpeed = constrain(mappedSpeed, 0, 255); // Clamp

      // Acitvate pins
      analogWrite(heartPin, mappedSpeed);
      analogWrite(LEDPin, mappedSpeed);
      Serial.println("success");
    }
  }
}