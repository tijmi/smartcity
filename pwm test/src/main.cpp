#include <Arduino.h>

#define Fan_Pin 10



void setup() {
  // put your setup code here, to run once:
  pinMode(Fan_Pin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n');
    if (message.startsWith("WIND")) {
      String speedStr = message.substring(12);
      int speed = speedStr.toInt();
      int mappedspeed = int(map(speed, 0, 8, 0, 255));
      if (speed >= 0 && speed <= 8) {
        analogWrite(Fan_Pin, mappedspeed);
        char buf[64];
        snprintf(buf, sizeof(buf), "success: %d", mappedspeed);
        Serial.println(buf);
      }
    }
  }
}


