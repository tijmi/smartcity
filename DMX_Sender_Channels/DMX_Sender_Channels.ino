#include <espDMX.h>

byte dmxData[2];

uint8_t level = 0;
bool up = true;

void setup() {
  dmxB.begin();
}

void loop() {
  dmxData[0] = level;
  dmxData[1] = level;
  dmxB.setChans(dmxData, 2, 141);   // channel 141

  if (up) {
    if (level < 255) level++;
    else up = false;
  } else {
    if (level > 0) level--;
    else up = true;
  }

  delay(20);
}