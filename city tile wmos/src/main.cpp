#include <Arduino.h>
#include <map>

#define DEVICE_ID "d1_sensor_01"
#define NO_CONNECTION 1024

#define s0 D4
#define s1 D3
#define s2 D2
#define s3 D1
#define sig A0


const int rangeCount = 14;
const int ranges[14][2] = {
  {0,   71},
  {72,  145},
  {146, 222},
  {223, 286},
  {287, 340},
  {341, 406},
  {407, 492},
  {493, 590},
  {591, 680},
  {681, 758},
  {759, 843},
  {844, 898},
  {899, 936},
  {937, 1024}
};

std::map<int, int> valueMap = {
	{1, 0}, {2, 0}, {3, 0}, {4, 0},
	{5, 0}, {6, 0}, {7, 0}, {8, 0},
	{9, 0}, {10, 0}, {11, 0}, {12, 0},
	{13, 0}, {14, 0}, {15, 0}, {16, 0}
};

int getID(int value) {
  if (value >= NO_CONNECTION) return -1;
  
  for (int i = 0; i < rangeCount; i++) {
    if (value >= ranges[i][0] && value <= ranges[i][1]) {
      return i; // ID is 0-indexed, change to i+1 if you want 1-indexed
    }
  }
  return -1; // not found
}

int readMux(int channel);

void setup() {
  Serial.begin(9600);

  pinMode(s0, OUTPUT);
  pinMode(s1, OUTPUT);
  pinMode(s2, OUTPUT);
  pinMode(s3, OUTPUT);

  digitalWrite(s0, LOW);
  digitalWrite(s1, LOW);
  digitalWrite(s2, LOW);
  digitalWrite(s3, LOW);

  pinMode(sig, INPUT);
}

void loop() {
  for (int i = 0; i < 16; i++) {
    int value = readMux(i);
    int id = getID(value);
    if (id != valueMap[i]) {
      valueMap[i] = id;
      char buf[64];
      snprintf(buf, sizeof(buf), "{\"tile_type\":%d,\"tile_id\":%d}", id, i);
      Serial.println(buf);
      delay(10);
    }
  }

}

int readMux(int channel) {
  int controlPin[] = { s0, s1, s2, s3 };

  int muxChannel[16][4] = {
    { 0, 0, 0, 0 },  //channel 0
    { 1, 0, 0, 0 },  //channel 1
    { 0, 1, 0, 0 },  //channel 2
    { 1, 1, 0, 0 },  //channel 3
    { 0, 0, 1, 0 },  //channel 4
    { 1, 0, 1, 0 },  //channel 5
    { 0, 1, 1, 0 },  //channel 6
    { 1, 1, 1, 0 },  //channel 7
    { 0, 0, 0, 1 },  //channel 8
    { 1, 0, 0, 1 },  //channel 9
    { 0, 1, 0, 1 },  //channel 10
    { 1, 1, 0, 1 },  //channel 11
    { 0, 0, 1, 1 },  //channel 12
    { 1, 0, 1, 1 },  //channel 13
    { 0, 1, 1, 1 },  //channel 14
    { 1, 1, 1, 1 }   //channel 15
  };

  //loop through the 4 sig (s0, s1, s2, s3)
  for (int i = 0; i < 4; i++) {
    digitalWrite(controlPin[i], muxChannel[channel][i]);
  }

  //read the value at the SIG pin
  int val = analogRead(sig);

  //return the value
  return val;
}