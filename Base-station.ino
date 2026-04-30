/*
===========================================================
Gateway Node for 16 Base-Stations
Author: Ahmed Ali
ahmed.a.radhi@nahrainuniv.edu.iq
Repository-ready Version
===========================================================

Description:
- Receives data from up to 16 Hybrid Sensor Nodes/Base-Stations
- Each node sends a vector [NodeID, lat, lon, temp, hum, CO]
- Gateway prints received vectors to USB Serial (for PC logging)
- nRF24L01+ radio module required
===========================================================
*/

#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

// Define nRF24 CE and CSN pins
RF24 radio(8, 7);

// Define 16 reading pipes (one per base-station)
const uint64_t pipes[16] = {
  0xF0F0F0F001, 0xF0F0F0F002, 0xF0F0F0F003, 0xF0F0F0F004,
  0xF0F0F0F005, 0xF0F0F0F006, 0xF0F0F0F007, 0xF0F0F0F008,
  0xF0F0F0F009, 0xF0F0F0F00A, 0xF0F0F0F00B, 0xF0F0F0F00C,
  0xF0F0F0F00D, 0xF0F0F0F00E, 0xF0F0F0F00F, 0xF0F0F0F099
};

void setup() {
  Serial.begin(115200);   // Initialize USB Serial
  while(!Serial) { }      // Wait for Serial monitor

  // Initialize nRF24 radio
  if(!radio.begin()){
    Serial.println("Radio hardware not responding!");
    while(1); // Stop if radio not found
  }

  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_250KBPS);

  // Open all 16 reading pipes
  for(int i=0; i<16; i++){
    radio.openReadingPipe(i+1, pipes[i]);
  }

  radio.startListening();
  Serial.println("Gateway ready to receive data from 16 base-stations...");
}

void loop() {
  uint8_t pipeNum;

  // Check if data available on any pipe
  if(radio.available(&pipeNum)){
    float vector[6]; // Expected: NodeID, lat, lon, temp, hum, CO
    radio.read(&vector, sizeof(vector));

    // Print received vector to Serial USB
    Serial.print("VECTOR:");
    for(int i=0; i<6; i++){
      Serial.print(vector[i], 3); // 3 decimal places
      if(i < 5) Serial.print(",");
    }
    
  }
}