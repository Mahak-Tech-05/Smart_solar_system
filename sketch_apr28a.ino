#include <Servo.h>

Servo solar;

// Pins
int ldrL = A0;
int ldrR = A1;
int tempPin = A2;
int voltPin = A3;
int ledPin = 7;

int pos = 90;

// ⏱️ Timer for 2 minutes
unsigned long previousTime = 0;
unsigned long interval = 10000; // 2 minutes

void setup() {
  Serial.begin(9600);

  solar.attach(9);
  solar.write(pos);

  pinMode(ledPin, OUTPUT);
}

void loop() {

  // 💡 LED blink (system running)
  digitalWrite(ledPin, HIGH);
  delay(50);
  digitalWrite(ledPin, LOW);

  // 🌗 Read LDR
  int left = analogRead(ldrL);
  int right = analogRead(ldrR);

  int diff = left - right;

  // ⚡ FAST TRACKING
  if (diff > 10) {
    pos += 20;
    if (pos > 180) pos = 180;
    solar.write(pos);
  } 
  else if (diff < -10) {
    pos -= 20;
    if (pos < 0) pos = 0;
    solar.write(pos);
  }

  // ⏱️ CHECK 2-MIN TIMER
  unsigned long currentTime = millis();

  if (currentTime - previousTime >= interval) {
    previousTime = currentTime;

    Serial.println("SWEEP START");

    // 🔁 Sweep 0 → 180
    for (pos = 0; pos <= 180; pos += 2) {
      solar.write(pos);
      delay(10);
    }

    // 🔁 Sweep 180 → 0
    for (pos = 180; pos >= 0; pos -= 2) {
      solar.write(pos);
      delay(10);
    }

    Serial.println("SWEEP END");

    pos = 90; // reset center
    solar.write(pos);
  }

  // 🌡 Temperature
  int t = analogRead(tempPin);
  float tempC = (t * 5.0 / 1023.0) * 100;

  // ⚡ Voltage
  int raw = analogRead(voltPin);
  float vout = raw * 5.0 / 1023.0;
  float vin = vout * 5.0;

  // 📡 Send data to Python
  Serial.print(left);
  Serial.print(",");
  Serial.print(right);
  Serial.print(",");
  Serial.print(tempC);
  Serial.print(",");
  Serial.println(vin);

  delay(300);
}