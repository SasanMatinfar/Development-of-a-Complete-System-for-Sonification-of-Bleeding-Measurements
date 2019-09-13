
//--------------------------------Geladene Bibliotheken---------------------------------------------

#include <Wire.h>                                               // Bibliothek für I2C-Bus
#include "AS7265X.h"                                            // Biblliothek für AMS AS7265X

//---------------------Sonstige Globale Variablen und Definitionen------------------------------

#define intPin 8

bool intFlag = false;
uint8_t MAJOR, PATCH, BUILD, status;
float    calData[18];
int16_t rawData[18];
uint16_t freq[18] = {610, 680, 730, 760, 810, 860, 560, 585, 645, 705, 900, 940, 410, 435, 460, 485, 510, 535}; // latest data sheet

/* choices are: 
 *  ledIndCurrent led_ind_1_mA, led_ind_2_mA, led_ind_4_mA, led_ind_8_mA
 *  ledDrvCurrent led_drv_12_5_mA, led_drv_25_mA, led_drv_50_mA, led_drv_100_mA
 */
uint8_t ledIndCurrent0 = led_ind_1_mA, ledDrvCurrent0 = led_drv_12_5_mA;
uint8_t ledIndCurrent1 = led_ind_1_mA, ledDrvCurrent1 = led_drv_12_5_mA;
uint8_t ledIndCurrent2 = led_ind_1_mA, ledDrvCurrent2 = led_drv_12_5_mA;

/* choices are:
 *  gain = gain_1x, gain_4x, gain_16x, gain_64x (default 16x)
 *  mode = mode0, mode1, mode2, mode3 (default mode2)
 *  intTime 1 - 255 (default 20) 
*   integration time = intTime * 2.8 milliseconds, so 20 * 2.8 ms == 56 ms default
*   maximum integration time = 714 ms
 */
uint8_t gain = gain_16x, mode = mode2, intTime = 36;

AS7265X AS7265X(intPin);

#define TCAADDR 0x70                                            // Definitionen für I2C Multiplexer

//-----------------------------Definitions for Shift Registers-----------------------------------------------------------------

#define SER    2                                                // data in                                    
#define SRCLK  A6                                               // shift register clock
#define SRCLR  A5                                               // clear shift register
#define RCLK   0                                                // storage register (sometimes called the latch pin)
#define OE     1                                                // enable output
#define TOTAL_SHIFT_PINS  16

//---------------------------Arduino setup routine-------------------------------------------------------

void setup() {

  Serial.begin(115200);
  delay(4000);

  pinMode(SER,OUTPUT);                                               // Initialize shift registers
  pinMode(SRCLK,OUTPUT);
  pinMode(SRCLR,OUTPUT);
  pinMode(RCLK,OUTPUT);
  pinMode(OE,OUTPUT);
  clearShiftRegisters();
  // turnOutputsOn();
 
  Wire.begin(); // set master mode 
  Wire.setClock(400000);      // I2C frequency at 400 kHz 
  delay(1000);

  pinMode(intPin, INPUT); // set up the interrupt pin

  tcaselect(0);
  setupAMS();
  tcaselect(1);
  setupAMS();
  tcaselect(2);
  setupAMS();

  attachInterrupt(intPin, myIntHandler, FALLING);
  AS7265X.getStatus();

  tcaselect(1);

}

//---------------------------Arduino loop routine-------------------------------------------------------

void loop() {


// Serial.println("SPECTROMETER 1");
// tcaselect(0);
// getData();


// middle LEDs
// lightOne(10); // blue
// lightOne(11); // red
lightOne(12); // white
// lightOne(13); // blue 760

// lightAll();
// Serial.println("SPECTROMETER 2");
getData();
turnOutputsOff();

//  Serial.println("SPECTROMETER 3");
// tcaselect(2);
// getData();´
  
}


//---------------------------I2C-Multiplexer Methode-------------------------------------------------------

void tcaselect(uint8_t i) {
  if (i > 7) return;
  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();  
}


// Useful functions
void myIntHandler ()
{
  intFlag = true;
}

// Setup AMS AS7265x

void setupAMS (){


  AS7265X.I2Cscan();
  Serial.println("I2C scan done");

  AS7265X.init(gain, mode, intTime);

  // get some information about the device hardware and firmware
  byte c = AS7265X.getDevType();
  Serial.print("AS72651 "); Serial.print("Device Type = 0x"); Serial.print(c, HEX);  Serial.println(" should be 0x40");
  Serial.println(" ");
  byte d = AS7265X.getHWVersion();
  Serial.print("AS72651 "); Serial.print("HW Version = 0x"); Serial.print(d, HEX); Serial.println(" should be 0x41"); 
  Serial.println(" ");

  uint16_t e = AS7265X.getFWMajorVersion();
  Serial.print("AS72651 "); Serial.print("FW Major Version = 0x"); Serial.print(e, HEX);
  Serial.println(" ");

  uint16_t f = AS7265X.getFWPatchVersion();
  Serial.print("AS72651 "); Serial.print("FW Patch Version = 0x"); Serial.print(f, HEX);
  Serial.println(" ");

  uint16_t g = AS7265X.getFWBuildVersion();
  Serial.print("AS72651 "); Serial.print("FW Build Version = 0x"); Serial.print(g, HEX);
  Serial.println(" ");

  delay(1000); 

  //Configure leds, for devices 0 (master), 1 and 2 (slaves)
  AS7265X.configureLed(ledIndCurrent0,ledDrvCurrent0, 0);
  AS7265X.disableIndLed(0);
  AS7265X.disableDrvLed(0);
  delay(100);
  AS7265X.configureLed(ledIndCurrent1,ledDrvCurrent1, 1);
  AS7265X.disableIndLed(1);
  AS7265X.enableDrvLed(1);
  delay(100);
  AS7265X.configureLed(ledIndCurrent2,ledDrvCurrent2, 2);
  AS7265X.disableIndLed(2);
  AS7265X.disableDrvLed(2);
  delay(100);

  
}

void getData() {


  status = AS7265X.getStatus();
  if(status & 0x02)
  {

//  AS7265X.readRawData(rawData);
//  for(int i = 0; i < 18; i++)
//  {
//   Serial.println(rawData[i]);
//  }
  delay(2000);
  AS7265X.readCalData(calData);
  for(int i = 0; i < 18; i++)
  {
   Serial.print(freq[i]); Serial.print(","); Serial.print(calData[i]); Serial.print(",");
  }
   Serial.println(" ");

//  for(int i = 0; i < 3; i++)
//  {
//   Serial.print("Temperature of device "); Serial.print(i); Serial.print (" is "); Serial.print(AS7265X.getTemperature(i), 0); Serial.println(" C");
//  }
//   Serial.println(" ");
 
  AS7265X.enableIndLed(0); delay(10); AS7265X.disableIndLed(0); // blink indicator led
  }
  
  delay(1000);
  
}



//---------------------------Light up 1 specified LED on external LED Board----------------------------------

void lightOne(int i){
    clearShiftRegisters();
    int data = HIGH;
    for(int j=0;j<i;++j) {
      shiftDataIn(data);  // first time here data will be HIGH.
      copyShiftToStorage();
      data = LOW;  // after first time it will always be LOW.
  }
  turnOutputsOn();
}

//---------------------------Light up all LEDs on external LED Board----------------------------------

void lightAll() { // light all
    clearShiftRegisters();
    int data = HIGH;
    for(int i=0;i<TOTAL_SHIFT_PINS;++i) {
      shiftDataIn(data);  // first time here data will be HIGH.
      copyShiftToStorage();
  }
  turnOutputsOn();
 
}

//---------------------------Shift register handling methods----------------------------------

// This doesn't change the value stored in the storage registers.
void turnOutputsOn() {
  digitalWrite(OE,LOW);
}

// This doesn't change the value stored in the storage registers.
void turnOutputsOff() {
  digitalWrite(OE,HIGH);
}

// clear the shift registers without affecting the storage registers.
void clearShiftRegisters() {
  digitalWrite(SRCLR,LOW);
  digitalWrite(SRCLR,HIGH);
}

// All the data in the shift registers moves over 1 unit and the new data goes in at shift register 0.
// The data that was in the shift register 7 goes to the next register (if any).
void shiftDataIn(int data) {
  digitalWrite(SER,data);
  digitalWrite(SRCLK,HIGH);
  digitalWrite(SRCLK,LOW);
}

// copy the 8 shift registers into the shift registers,
// which changes the output voltage of the pins.
void copyShiftToStorage() {
  digitalWrite(RCLK,HIGH);
  digitalWrite(RCLK,LOW);
}
