/*
===========================================================
 Hybrid Node (Relay + Smart Sensor Node) with Node ID
===========================================================

Author: Ahmed Ali
ahmed.a.radhi@nahrainuniv.edu.iq
Features:
✔ Receives data from 5 sensor nodes (multi-pipe)
✔ Immediately forwards received data to Gateway
✔ Applies local MLR fire detection
✔ Sends its own data if fire detected
✔ Transmission format: Vector [1x6] = [NodeID, lat, lon, temp, hum, CO]
===========================================================
*/

#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <math.h>
#include <DHT11.h>

//================ RF =================
RF24 radio(8, 7);

// Pipes
const uint64_t pipe1 = 0xF0F0F0F0A1;
const uint64_t pipe2 = 0xF0F0F0F0A2;
const uint64_t pipe3 = 0xF0F0F0F0A3;
const uint64_t pipe4 = 0xF0F0F0F0A4;
const uint64_t pipe5 = 0xF0F0F0F0A5;

// Gateway
const uint64_t gatewayPipe = 0xF0F0F0F099;

//================ Node Info =================
float latitude = 36.900;
float longitude = 30.710;
const uint8_t localNodeID = 6;

//================ DHT11 =================
DHT11 dht11(2);

//================ MQ7 =================
#define CO_PIN A0
float RL = 10.0;
float R0 = 1.02;   // Calibration

//================ MLR =================
float b0 = -26.885;
float b1 = -0.4798;
float b2 = 0.267;
float b3 = 6.814;

//================ Functions =================
float sigmoid(float x) {
  return 1.0 / (1.0 + exp(-x));
}

//===================================================
void setup()
{
  Serial.begin(9600);

  radio.begin();
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_250KBPS);

  radio.openReadingPipe(1, pipe1);
  radio.openReadingPipe(2, pipe2);
  radio.openReadingPipe(3, pipe3);
  radio.openReadingPipe(4, pipe4);
  radio.openReadingPipe(5, pipe5);

  radio.startListening();

  pinMode(CO_PIN, INPUT);

 

  Serial.println("Hybrid Node Ready (MQ7 + DHT11)...");
}

//===================================================
void loop()
{
  uint8_t pipeNum;

  //==============================
  // Receive & Forward
  //==============================
  if (radio.available(&pipeNum))
  {
    float incoming[5];
    radio.read(&incoming, sizeof(incoming));

    uint8_t nodeID = pipeNum;

    float vector[6];
    vector[0] = nodeID;
    for (int i = 0; i < 5; i++)
      vector[i + 1] = incoming[i];

    Serial.print("Node");
    Serial.println(nodeID);

    radio.stopListening();
    radio.openWritingPipe(gatewayPipe);
    radio.write(&vector, sizeof(vector));
    radio.startListening();
  }

  //==============================
  // MQ7 CO Calculation
  //==============================
  float sum = 0;
  for(int i = 0; i < 10; i++){
    sum += analogRead(CO_PIN);
    delay(5);
  }

  float adc = sum / 10.0;
  float Vout = adc * (5.0 / 1023.0);

  if (Vout < 0.1) Vout = 0.1;

  float RS = ((5.0 - Vout) / Vout) * RL;
  float ratio = RS / R0;

  float co_ppm = 93.89 * pow(ratio, -1.549);
  if (co_ppm < 0) co_ppm = 0;

  //==============================
  // DHT11 Reading
  //==============================
 // Read sensor data
  float temperature = dht11.readTemperature();
  float humidity = dht11.readHumidity();
  //==============================
  // MLR Fire Detection
  //==============================
  float z = b0 + b1*temperature + b2*humidity + b3*co_ppm;
  float probability = sigmoid(z);

 // ==============================
  // Debug output
  // ==============================
  Serial.print("Temp: "); Serial.print(temperature);
  Serial.print(" | Hum: "); Serial.print(humidity);
  Serial.print(" | CO: "); Serial.print(co_ppm);
  Serial.print(" | Prob: "); Serial.println(probability);

  //==============================
  // Send if Fire Detected
  //==============================
  if (probability > 0.5)
  {
    float localVector[6];
    localVector[0] = localNodeID;
    localVector[1] = latitude;
    localVector[2] = longitude;
    localVector[3] = temperature;
    localVector[4] = humidity;
    localVector[5] = co_ppm;

    radio.stopListening();
    radio.openWritingPipe(gatewayPipe);
    radio.write(&localVector, sizeof(localVector));
    radio.startListening();

    Serial.println("Fire Sent to Gateway");
  }

  delay(600000);
}