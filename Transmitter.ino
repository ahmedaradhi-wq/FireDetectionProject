/*
===========================================================
 IoT-Based Wildfire Early Detection Node (Transmitter)
===========================================================

Author: Ahmed Ali  
ahmed.a.radhi@nahrainuniv.edu.iq
Description:
This program implements a low-power IoT sensor node for early wildfire detection.
The system uses:

- nRF24L01 for wireless communication
- DHT11 sensor for temperature and humidity
- MQ sensor (analog) for CO detection
- MLR (Multiple Logistic Regression) model for local decision-making

Key Features:
✔ Edge intelligence using MLR model
✔ Data transmission ONLY when fire is suspected
✔ nRF24L01 enters power-down mode to save energy
✔ Periodic sensing (every 1 hour)

Data Packet Format:
[0] NodeID
[1] Latitude
[2] Longitude
[3] Temperature (°C)
[4] Humidity (%)
[5] CO level (approx.)

===========================================================
*/

#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <DHT11.h>
#include <math.h>

//================ MQ7 =================
#define CO_PIN A0
float RL = 10.0;
float R0 = 1.02;   // Calibration


// Initialize RF module (CE, CSN)
RF24 radio(10, 9);

// Initialize DHT11 sensor (pin 2)
DHT11 dht11(2);

// Communication pipe
const uint64_t pipe2 = 0xF0F0F0F0A1;

// Node GPS location
float latitude = 36.899;
float longitude = 30.713;
const uint8_t NodeID = 1;

// Data array (unchanged structure)
float data[6];  

// ==============================
//================ MLR =================
float b0 = -26.885;
float b1 = -0.4798;
float b2 = 0.267;
float b3 = 6.814;

// ==============================
// Sigmoid function
// ==============================
float sigmoid(float x) {
  return 1.0 / (1.0 + exp(-x));
}

// ==============================
void setup()
{
  Serial.begin(9600);

  // Initialize RF module
  radio.begin();
  radio.openWritingPipe(pipe2);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_250KBPS);

  pinMode(CO_PIN, INPUT);
}

// ==============================
void loop()
{
  //  Sampling every 1 hour (3600000 ms)
  delay(3600000);

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
  // ==============================
  // MLR-based fire prediction
  // ==============================
  float z = b0 + (b1 * temperature) + (b2 * humidity) + (b3 * co_ppm);
  float probability = sigmoid(z);

  // Fire decision threshold
  int fire_flag = (probability > 0.5) ? 1 : 0;

  // ==============================
  //  Transmit only if fire detected
  // ==============================
  if (fire_flag == 1)
  {
    radio.powerUp();
    radio.stopListening();

    // Prepare data packet
    data[0] = NodeID;
    data[1] = latitude;
    data[2] = longitude;
    data[3] = temperature;
    data[4] = humidity;
    data[5] = co_ppm;

    // Send data
    radio.write(&data, sizeof(data));

    Serial.println("Fire detected → Data transmitted");

    // Enter low-power mode after transmission
    radio.powerDown();
  }
  else
  {
    Serial.println("Normal condition → NRF in sleep mode");

    // Save energy when no fire
    radio.powerDown();
  }

  // ==============================
  // Debug output
  // ==============================
  Serial.print("Temp: "); Serial.print(temperature);
  Serial.print(" | Hum: "); Serial.print(humidity);
  Serial.print(" | CO: "); Serial.print(co_ppm);
  Serial.print(" | Prob: "); Serial.println(probability);
}