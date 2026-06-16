#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>

#include <Servo.h>

#include <ArduinoJson.h>

#define TFT_CS 16   //for D1 mini or TFT I2C Connector Shield (V1.1.0 or later)
#define TFT_DC 15   //for D1 mini or TFT I2C Connector Shield (V1.1.0 or later)
#define TFT_RST -1  //for D1 mini or TFT I2C Connector Shield (V1.1.0 or later)

#define pin_blueIn 5   // GPIO
#define pin_blueOut 2  // GPIO
#define pin_redIn A0   // GPIO //4
#define pin_redOut 0   // GPIO

#define pin_servo 4  // GPIO //1

Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC, TFT_RST);
Servo myservo;

bool debug = false;
bool servoUp = true;

bool bluePressed = false;
bool redPressed = false;

unsigned long prev_debug = 0;
unsigned long prev_buttons = 0;
unsigned long prev_servo = 0;
const unsigned long interval_debug = 500;
const unsigned long interval_servo = 10;
const unsigned long interval_buttons = 15;

int Zi_5110_strength = 99;
int Zi_5110_planes = 99;
int Zi_5110_normalized = 99;
int Zi_5067_strength = 99;
int Zi_5067_planes = 99;
int Zi_5067_normalized = 99;

int servoPos = 90;
int servoWantedPos = 90;

void setup() {
  Serial.begin(115200);
  Serial.print("starting setup");

  tft.begin();
  screenDiagnostics();

  // Input with internal pull-up
  pinMode(pin_blueIn, INPUT_PULLUP);
  pinMode(pin_redIn, INPUT_PULLUP);

  pinMode(pin_blueOut, OUTPUT);
  pinMode(pin_redOut, OUTPUT);

  myservo.attach(pin_servo);
  myservo.write(90);

  tft.setRotation(1);
  drawInitScreen();

  Serial.print("Setup Complete!");
}

void loop() {
  unsigned long currentMillis = millis();

  if (debug && (currentMillis - prev_debug >= interval_debug)) {
    prev_debug = currentMillis;
    if (servoUp) {
      servoWantedPos += 5;
    } else {
      servoWantedPos -= 5;
    }

    if (servoUp && servoWantedPos > 110) {
      servoUp = false;
    } else if (!servoUp && servoWantedPos < 70) {
      servoUp = true;
    }

    updateScreen(servoPos, servoWantedPos);

  } else if (Serial.available()) {
    serialCommunication();
    updateState();
  }

  if (currentMillis - prev_buttons >= interval_buttons) {
    prev_buttons = currentMillis;

    bool blueNewPressed = buttonState(pin_blueIn);
    bool redNewPressed = analogButtonState(pin_redIn);

    buttonLight(blueNewPressed, pin_blueOut);
    buttonLight(redNewPressed, pin_redOut);

    if (bluePressed != blueNewPressed || redPressed != redNewPressed) {
      updateState();
    }

    bluePressed = blueNewPressed;
    redPressed = redNewPressed;
  }

  if (currentMillis - prev_servo >= interval_servo) {
    prev_servo = currentMillis;
    moveServo();
  }
}

void updateState() {
  int Zi_5110_strength_local = 99;
  int Zi_5067_strength_local = 99;

  if (bluePressed) {
    Zi_5110_strength_local = Zi_5110_normalized;
    Zi_5067_strength_local = Zi_5067_normalized;
  } else {
    Zi_5110_strength_local = Zi_5110_strength;
    Zi_5067_strength_local = Zi_5067_strength;
  }

  if (redPressed && Zi_5110_planes != 0 && Zi_5067_planes != 0) {
    Zi_5110_strength_local = int(Zi_5110_strength_local / Zi_5110_planes);
    Zi_5067_strength_local = int(Zi_5067_strength_local / Zi_5067_planes);
  }
  if (Zi_5110_planes != 0 && Zi_5067_planes != 0) {
    updateServoPos(Zi_5110_strength_local, Zi_5067_strength_local);
  } else {
    updateServoPos(1, 1);
  }

  updateScreen(Zi_5110_strength_local, Zi_5067_strength_local);
}

void updateServoPos(int Zi_5110_strength_local, int Zi_5067_strength_local) {
  float a = float(Zi_5110_strength_local);
  float b = float(Zi_5067_strength_local);

  float score = (a - b) / (abs(a) + abs(b) + 1.0f);  // -1 to +1

  float pos_local = 90.0f + score * 70.0f;
  servoWantedPos = int(constrain(pos_local, 30, 160));
  // servoWantedPos = constrain(pos_local, 70, 110);
  //servoWantedPos = mapServoPos(float(Zi_5110_strength_local) / float(Zi_5067_strength_local));
}

void updateScreen(int Zi_5110_strength_local, int Zi_5067_strength_local) {
  // Clear old values
  tft.fillRect(10, 120, 100, 40, ILI9341_BLACK);   // Left value area
  tft.fillRect(220, 120, 100, 40, ILI9341_BLACK);  // Right value area

  tft.fillRect(10, 180, 100, 40, ILI9341_BLACK);   // Left value area
  tft.fillRect(220, 180, 100, 40, ILI9341_BLACK);  // Right value area

  drawValues(Zi_5110_strength_local, Zi_5067_strength_local);
}

void drawValues(int Zi_5110_strength_local, int Zi_5067_strength_local) {
  // Draw updated values
  tft.setTextSize(4);
  tft.setTextColor(ILI9341_WHITE);

  tft.setCursor(10, 120);
  tft.print(Zi_5110_strength_local);

  tft.setCursor(220, 120);
  tft.print(Zi_5067_strength_local);

  tft.setCursor(10, 180);
  tft.print(Zi_5110_planes);

  tft.setCursor(220, 180);
  tft.print(Zi_5067_planes);
}

void drawInitScreen() {
  tft.fillScreen(ILI9341_BLACK);

  tft.setTextColor(ILI9341_WHITE);
  tft.setTextSize(3);

  tft.setCursor(10, 30);
  tft.print("Zi");

  tft.setCursor(10, 60);
  tft.print("5110");

  tft.setCursor(220, 30);
  tft.print("Zi");

  tft.setCursor(220, 60);
  tft.print("5067");

  tft.setTextSize(2);
  tft.setCursor(10, 100);
  tft.print("Strength  [dBm]");

  tft.setCursor(220, 100);
  tft.print("Strength");

  tft.setCursor(10, 160);
  tft.print("Planes");

  tft.setCursor(220, 160);
  tft.print("Planes");

  drawValues(Zi_5110_strength, Zi_5067_strength);
}

void moveServo() {
  if (servoPos < servoWantedPos) {
    servoPos += 1;
    myservo.write(servoPos);
  } else if (servoPos > servoWantedPos) {
    servoPos -= 1;
    myservo.write(servoPos);
  }
}

bool buttonState(uint8_t pin_button) {
  if (digitalRead(pin_button) == LOW) {
    return false;
  } else {
    return true;
  }
}

bool analogButtonState(uint8_t pin_button) {
  // Unpressed is typically 1024; pressed is 0
  if (analogRead(pin_button) < 500) {
    return false;
  } else {
    return true;
  }
}

void buttonLight(bool bool_button, uint8_t pin_button) {
  if (bool_button == true) {
    digitalWrite(pin_button, HIGH);
  } else {
    digitalWrite(pin_button, LOW);
  }
}

void screenDiagnostics() {
  // read diagnostics (optional but can help debug problems)
  uint8_t x = tft.readcommand8(ILI9341_RDMODE);
  Serial.print("Display Power Mode: 0x");
  Serial.println(x, HEX);
  x = tft.readcommand8(ILI9341_RDMADCTL);
  Serial.print("MADCTL Mode: 0x");
  Serial.println(x, HEX);
  x = tft.readcommand8(ILI9341_RDPIXFMT);
  Serial.print("Pixel Format: 0x");
  Serial.println(x, HEX);
  x = tft.readcommand8(ILI9341_RDIMGFMT);
  Serial.print("Image Format: 0x");
  Serial.println(x, HEX);
  x = tft.readcommand8(ILI9341_RDSELFDIAG);
  Serial.print("Self Diagnostic: 0x");
  Serial.println(x, HEX);

  Serial.println(F("Benchmark                Time (microseconds)"));
  delay(10);
  Serial.print(F("Screen fill              "));
  Serial.println(testFillScreen());
  delay(500);
}

unsigned long testFillScreen() {
  unsigned long start = micros();
  tft.fillScreen(ILI9341_BLACK);
  yield();
  tft.fillScreen(ILI9341_RED);
  yield();
  tft.fillScreen(ILI9341_GREEN);
  yield();
  tft.fillScreen(ILI9341_BLUE);
  yield();
  tft.fillScreen(ILI9341_BLACK);
  yield();
  return micros() - start;
}

void serialCommunication() {
  String message = Serial.readStringUntil('\n');
  JsonDocument data;
  DeserializationError error = deserializeJson(data, message);

  Serial.print("Received: ");
  Serial.println(message);

  Zi_5110_strength = data["Zi-5110_strength"];
  Zi_5110_planes = data["Zi-5110_planes"];
  Zi_5110_normalized = data["Zi-5110_normalized"];
  Zi_5067_strength = data["Zi-5067_strength"];
  Zi_5067_planes = data["Zi-5067_planes"];
  Zi_5067_normalized = data["Zi-5067_normalized"];
}

int mapServoPos(float x) {
  float pos = 20 * (1.0 - log(x) / log(5.0)) + 80;
  return int(pos);
}