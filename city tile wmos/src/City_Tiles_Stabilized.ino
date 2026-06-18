#include <Arduino.h>
#include <map>

#define DEVICE_ID "d1_sensor_01"
#define NO_CONNECTION 1024

#define s0 D4
#define s1 D3
#define s2 D2
#define s3 D1
#define sig A0

#define number_of_tracked_readings 5


const int rangeCount = 14;
const int ranges[14][2] = {
  { 0, 71 },
  { 72, 145 },
  { 146, 222 },
  { 223, 286 },
  { 287, 340 },
  { 341, 406 },
  { 407, 492 },
  { 493, 590 },
  { 591, 680 },
  { 681, 758 },
  { 759, 843 },
  { 844, 898 },
  { 899, 936 },
  { 937, 1024 }
};

std::map<int, int> valueMap = {
  { 1, 0 }, { 2, 0 }, { 3, 0 }, { 4, 0 }, { 5, 0 }, { 6, 0 }, { 7, 0 }, { 8, 0 }, { 9, 0 }, { 10, 0 }, { 11, 0 }, { 12, 0 }, { 13, 0 }, { 14, 0 }, { 15, 0 }, { 16, 0 }
};

int readings_list[16][number_of_tracked_readings];

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

  initiate_readings_list(-1);  //-1 is for 'no tile detected'
}

void loop() {
  read_values();
  send_values();
}

void send_values() {
  for (int i = 0; i < 16; i++) {

    int id = get_most_frequent_id(readings_list[i]);

    // if value has updated
    if (id != valueMap[i]) {
      valueMap[i] = id;
      char buf[64];
      snprintf(buf, sizeof(buf), "{\"tile_type\":%d,\"tile_id\":%d}", id, i);
      Serial.println(buf);
    }
  }
}

int get_most_frequent_id(int id_list[3]) {
  int maxcount = 0;
  int id;

  for (int i = 0; i < number_of_tracked_readings; i++) {
    int count = 0;
    for (int j = 0; j < number_of_tracked_readings; j++) {
      if (id_list[i] == id_list[j])
        count++;
    }

    // If count is greater or if count
    // is same but value is bigger: || (count == maxcount && arr[i] > id))
    if (count > maxcount) {
      maxcount = count;
      id = id_list[i];
    }
  }
  return id;
}

void read_values() {
  for (int i = 0; i < 16; i++) {
    int value = avgReadMux(i);
    int id = getID(value);

    for (int j = 1; j < number_of_tracked_readings; j++) {
      readings_list[i][j] = readings_list[i][j + 1];
    }
    readings_list[i][0] = id;
  }
}

int avgReadMux(int channel) {
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
  int controlPin[] = { s0, s1, s2, s3 };

  // set MUX channel
  for (int i = 0; i < 4; i++) {
    digitalWrite(controlPin[i], muxChannel[channel][i]);
  }

  int n_readings = 2;
  int readings = 0;

  for (int j = 0; j < n_readings; j++) {
    delay(5);
    readings += analogRead(sig);
  }
  int reading = readings / n_readings;
  return reading;
}

int getID(int value) {
  if (value >= NO_CONNECTION) return -1;

  for (int i = 0; i < rangeCount; i++) {
    if (value >= ranges[i][0] && value <= ranges[i][1]) {
      return i;  // ID is 0-indexed, change to i+1 if you want 1-indexed
    }
  }
  return -1;  // not found
}

void initiate_readings_list(int none_index) {
  for (int i = 0; i < 16; i++) {
    for (int j = 0; j < 3; j++) {
      readings_list[i][j] = none_index;
    }
  }
}