/*
 *    FILE: turbidostat.ino
 *  AUTHOR: Christian Wohltat, Stefan Hoffman
 *    DATE: 2019-06-09
 *
 */ 
 
#define TURBIDOSTAT_VERSION  "0.405"
#define NO_PORTB_PINCHANGES // to indicate that port b will not be used for pin change interrupts
#define NO_PORTC_PINCHANGES // to indicate that port c will not be used for pin change interrupts


#include "PinChangeInt.h"
#include <EEPROM.h>
#include <avr/eeprom.h>
#include <SerialCommand.h>

// PINS
#define LEDPIN        13
#define SENSOR_A_PIN  2
#define SENSOR_B_PIN  3
#define HALLPIN       4 
#define PUMPPIN       5
#define STIRRERPIN    6
#define AUXPIN        9
#define LASERPIN      AUXPIN
#define AIRPUMPPIN    10
#define VOLTAGEPIN    A4

// eeprom addresses 
#define EEPROM_OFFSET                   0
#define EEPROM_TARGET_I                (0*sizeof(uint32_t))
#define EEPROM_I0                      (1*sizeof(uint32_t))
#define EEPROM_PUMP_MODE               (2*sizeof(uint32_t))
#define EEPROM_PUMP_POWER              (3*sizeof(uint32_t))
#define EEPROM_AIRPUMP_POWER           (4*sizeof(uint32_t))
#define EEPROM_PUMP_DURATION           (5*sizeof(uint32_t))
#define EEPROM_PUMP_INTERVAL           (6*sizeof(uint32_t))
#define EEPROM_STIRRER_TARGET_SPEED    (7*sizeof(uint32_t))
#define EEPROM_LASER_POWER             (9*sizeof(uint32_t))
#define EEPROM_SERIAL0                 (64*sizeof(uint32_t))
#define EEPROM_SERIAL1                 (65*sizeof(uint32_t))
#define EEPROM_DEVICE_NAME             (128*sizeof(uint32_t))


// Serial connection
SerialCommand sCmd;     

// light sensors variables
volatile uint32_t cnta = 0;
volatile uint32_t cntb = 0;
uint32_t oldcnta = 0;
uint32_t oldcntb = 0;
uint32_t t = 0;

// OD measurement parameter
float targetOD = 1;
float OD = 0;
float Ia = 0;         // current intensity of sensor A in uW/m2
float Ib = 0;         // current intensity of sensor B in uW/m2
float I = 0;         // current intensity in uW/m2
float targetI = 0;   // target intensity in uW/m2
float I0 = 0;       // zero intensity in uW/m2

volatile bool halted = false;

// pump variables
uint32_t pumpMode = 0;
uint32_t pumpPower = 255;
uint32_t airpumpPower = 0;
uint32_t pumpDuration = 1000;  // in ms
uint32_t pumpInterval = 5000;     // in ms
byte thresholdCnt = 0;        
#define NTIMESTHRESHOLD  3
#define PUMP_MODE_AUTOMATIC   0
#define PUMP_MODE_MANUAL      1

// stirrer parameter
#define STIRRER_FIXPOINT_COEF (10000L)
#define STIRRER_MAX (150 * STIRRER_FIXPOINT_COEF)
// stirrer variables
volatile uint32_t stirrerLastTime = 0;
volatile uint32_t stirrerLastPeriod = 99999;
volatile int32_t stirrerOut = 30*10000;
uint32_t stirrerTargetSpeed = 800;  // in 1/min

// volatile int32_t laserPower = 0;
uint32_t laserPower = 0;

// device ID number
uint32_t device_id0, device_id1;
char device_name[128] = "device name";

//////////////////////////////
//
// PROTOTYPES 
//
//////////////////////////////
uint32_t   getSerialIntArgument();
void       setPwmFrequency(int pin, int divisor);
double     getArduinoTemp(void);

constexpr uint16_t isr_throttling_limit = 20000;
bool sensor_a_isr_throttle = false;
bool sensor_b_isr_throttle = false;

// INTERRUPT ROUTINES
void isrSensorA(){
  cnta++;
  if(cnta > 50000){
    detachInterrupt(0);
    sensor_a_isr_throttle = true;
  }
}

void isrSensorB(){
  cntb++;
  if(cntb > 1000){
    // detachInterrupt(1);
    sensor_b_isr_throttle = true;
    analogWrite(LASERPIN, 0);
  }
}

#define PWM_DEVISOR       1
#define TIME_FACTOR       (64/PWM_DEVISOR)
#define now               ((uint32_t) micros() / TIME_FACTOR)
#define MICROS_MAX_VALUE  (1L << 26) 

volatile bool run_stirrer_control = true;

void isr_hall_sensor(){
  uint32_t _stirrerLastPeriod = (now - stirrerLastTime) % MICROS_MAX_VALUE;
  if(_stirrerLastPeriod > 1000){
    run_stirrer_control = true;
    stirrerLastPeriod = _stirrerLastPeriod;
    stirrerLastTime = now;
    // Serial.println("----------------------------------------------------");
    // stirrer_control();
  }
}



// activate medium pump
void pumpOn(byte power=255){
  analogWrite(PUMPPIN, power);
}

void pumpOff(){
  analogWrite(PUMPPIN, 0);
}

// activate medium pump
void airpumpOn(byte power=255){
  analogWrite(AIRPUMPPIN, power);
}

void airpumpOff(){
  analogWrite(AIRPUMPPIN, 0);
}

void stirrerOff(){
  analogWrite(STIRRERPIN, 0);
}

void laserOff(){
  analogWrite(LASERPIN, 0);
}



void stirrer_control(){
  uint32_t stirrerTargetPeriod = (STIRRER_FIXPOINT_COEF*100*60) / stirrerTargetSpeed;
  // global varible stirrerLastPeriod
  static uint32_t uOld;
  
  int32_t u = stirrerLastPeriod - stirrerTargetPeriod;
  int32_t du = u - uOld;
  uOld = u;
  
  stirrerOut += u*1 - du/10;  
  stirrerOut = constrain(stirrerOut, 0, STIRRER_MAX);

  analogWrite(STIRRERPIN, stirrerOut/STIRRER_FIXPOINT_COEF);
}

void laser_control(){
  attachInterrupt(0, isrSensorA, RISING);
  attachInterrupt(1, isrSensorB, RISING);

  // turn on the sensor isr again
  if(sensor_a_isr_throttle){
    attachInterrupt(0, isrSensorA, RISING);
    // Serial.println("Sensor A Throttle");
    sensor_a_isr_throttle = false;
  }
  if(sensor_b_isr_throttle){
    attachInterrupt(1, isrSensorB, RISING);
    // Serial.println("Sensor B Throttle");
    sensor_b_isr_throttle = false;
    analogWrite(LASERPIN, laserPower);
  }
}

// void laser_control(){
//   uint32_t laserTargetIntensity = 40000;
//   static uint32_t uOld = 50000;
  
//   int32_t u = cntb - laserTargetIntensity;
//   int32_t du = u - uOld;
  
//   Serial.print("u: ");  
//   Serial.print(u);  
//   Serial.print(", uOld: ");  
//   Serial.print(uOld);  
//   Serial.print(", du:");  
//   Serial.print(du);  
//   uOld = u;

//   laserPower -= u/1000 - du/20000;  
//   Serial.print(", laserPower: ");  
//   Serial.print(laserPower);  
//   laserPower = constrain(laserPower, 0, 255);
//   Serial.print(", laserPower_: ");  
//   Serial.print(laserPower);
//   Serial.println("");  
//   Serial.println("");  

//   // analogWrite(LASERPIN, laserPower);
//   // analogWrite(LASERPIN, 100);
// }


/*
Name:           Timer2init
Function:       Init timer 2 to interrupt periodically. Call this from 
                the Arduino setup() function.
Description:    The pre-scaler and the timer count divide the timer-counter
                clock frequency to give a timer overflow interrupt rate:
                Interrupt rate =  16MHz / (prescaler * (255 - TCNT2))

        TCCR2B[b2:0]   Prescaler    Freq [KHz], Period [usec] after prescale
          0x0            (TC stopped)     0         0
          0x1                1        16000.        0.0625
          0x2                8         2000.        0.500
          0x3               32          500.        2.000
          0x4               64          250.        4.000
          0x5              128          125.        8.000
          0x6              256           62.5      16.000
          0x7             1024           15.625    64.000
*/
void Timer2init() {
    // Setup Timer2 overflow to fire every 8ms (125Hz)
    //   period [sec] = (1 / f_clock [sec]) * prescale * (255-count)
    //                  (1/16000000)  * 1024 * (255-130) = .008 sec

    TCCR2B = 0x00;        // Disable Timer2 while we set it up

    TCNT2  = 130;         // Reset Timer Count  (255-130) = execute ev 125-th T/C clock
    TIFR2  = 0x00;        // Timer2 INT Flag Reg: Clear Timer Overflow Flag
    TIMSK2 = 0x01;        // Timer2 INT Reg: Timer2 Overflow Interrupt Enable
    TCCR2A = 0x00;        // Timer2 Control Reg A: Wave Gen Mode normal
    TCCR2B = 0x05;        // Timer2 Control Reg B: Timer Prescaler set to 1024
}

extern volatile uint32_t msecs = 0;

// Handles the Timer2-overflow interrupt 
ISR(TIMER2_OVF_vect) {
  static unsigned char count;            // interrupt counter

  //if( (++count & 0x01) == 0 )     // bump the interrupt counter
    ++msecs;              // & count uSec every other time.
  TCNT2 = 256-125;                // reset counter every 125th time (125*4us = 1ms)
  TIFR2 = 0x00;                   // clear timer overflow flag
};


void eeprom_save(){
  eeprom_write_block((const void*)&targetI,           (void*)EEPROM_TARGET_I + EEPROM_OFFSET,           sizeof(uint32_t));
  eeprom_write_block((const void*)&I0,                (void*)EEPROM_I0 + EEPROM_OFFSET,                sizeof(uint32_t));
  eeprom_write_block((const void*)&stirrerTargetSpeed,(void*)EEPROM_STIRRER_TARGET_SPEED + EEPROM_OFFSET,        sizeof(uint32_t));
  eeprom_write_block((const void*)&pumpDuration,      (void*)EEPROM_PUMP_DURATION + EEPROM_OFFSET, sizeof(uint32_t));
  eeprom_write_block((const void*)&pumpInterval,      (void*)EEPROM_PUMP_INTERVAL + EEPROM_OFFSET,     sizeof(uint32_t));
  eeprom_write_block((const void*)&pumpMode,          (void*)EEPROM_PUMP_MODE + EEPROM_OFFSET,          sizeof(uint32_t));
  eeprom_write_block((const void*)&pumpPower,         (void*)EEPROM_PUMP_POWER + EEPROM_OFFSET,         sizeof(uint32_t));
  eeprom_write_block((const void*)&airpumpPower,      (void*)EEPROM_AIRPUMP_POWER + EEPROM_OFFSET,      sizeof(uint32_t));
  eeprom_write_block((const void*)&laserPower,        (void*)EEPROM_LASER_POWER + EEPROM_OFFSET,      sizeof(uint32_t));
  eeprom_write_block((const void*)&device_name,       (void*)EEPROM_DEVICE_NAME + EEPROM_OFFSET,        sizeof(device_name));
}

void eeprom_load(){
  // load parameter from eeprom
  eeprom_read_block(&targetI,           (const void*)EEPROM_TARGET_I + EEPROM_OFFSET,          sizeof(uint32_t));
  eeprom_read_block(&I0,                (const void*)EEPROM_I0 + EEPROM_OFFSET,                sizeof(uint32_t));
  targetOD = pow(10, (float)I0/targetI);
  
  eeprom_read_block(&stirrerTargetSpeed,(const void*)EEPROM_STIRRER_TARGET_SPEED + EEPROM_OFFSET,        sizeof(uint32_t));
  eeprom_read_block(&pumpDuration,      (const void*)EEPROM_PUMP_DURATION + EEPROM_OFFSET,      sizeof(uint32_t));
  eeprom_read_block(&pumpInterval,      (const void*)EEPROM_PUMP_INTERVAL + EEPROM_OFFSET,      sizeof(uint32_t));
  eeprom_read_block(&pumpMode,          (const void*)EEPROM_PUMP_MODE + EEPROM_OFFSET,          sizeof(uint32_t));
  eeprom_read_block(&pumpPower,         (const void*)EEPROM_PUMP_POWER + EEPROM_OFFSET,         sizeof(uint32_t));
  eeprom_read_block(&airpumpPower,      (const void*)EEPROM_AIRPUMP_POWER + EEPROM_OFFSET,      sizeof(uint32_t));
  eeprom_read_block(&laserPower,        (const void*)EEPROM_LASER_POWER + EEPROM_OFFSET,        sizeof(uint32_t));
  eeprom_read_block((void*)&device_id0, (const void*)EEPROM_SERIAL0 + EEPROM_OFFSET,            sizeof(device_id0));
  eeprom_read_block((void*)&device_id1, (const void*)EEPROM_SERIAL1 + EEPROM_OFFSET,            sizeof(device_id1));
  eeprom_read_block((void*)&device_name,(const void*)EEPROM_DEVICE_NAME + EEPROM_OFFSET,        sizeof(device_name));
 
  // set default values if eeprom values are "undefined" and save it to eeprom
  // this is propably only done once when eeprom is empty
  if (stirrerTargetSpeed > 3000){
    stirrerTargetSpeed = 800;
    eeprom_write_block(&stirrerTargetSpeed, (void*)EEPROM_STIRRER_TARGET_SPEED + EEPROM_OFFSET,          sizeof(uint32_t));
  }
  if (pumpDuration > 100000){
    pumpDuration = 1000;
    eeprom_write_block(&pumpDuration, (void*)EEPROM_PUMP_DURATION + EEPROM_OFFSET,   sizeof(uint32_t));
  }
  if (pumpInterval > 1000000){
    pumpInterval = 5000;
    eeprom_write_block(&pumpInterval,     (void*)EEPROM_PUMP_INTERVAL + EEPROM_OFFSET,       sizeof(uint32_t));
  }
  if (pumpPower > 255){
    pumpPower = 255;
    eeprom_write_block(&pumpPower,        (void*)EEPROM_PUMP_POWER + EEPROM_OFFSET,           sizeof(uint32_t));
  }
  if (airpumpPower > 255){
    airpumpPower = 255;
    eeprom_write_block(&airpumpPower,        (void*)EEPROM_AIRPUMP_POWER + EEPROM_OFFSET,           sizeof(uint32_t));
  }
  if (laserPower > 255){
    laserPower = 125;
    eeprom_write_block(&laserPower,        (void*)EEPROM_LASER_POWER + EEPROM_OFFSET,           sizeof(uint32_t));
  }
}

void printSettings(){
  Serial.print("deviceName: ");
  Serial.println(device_name);
  Serial.print("deviceID: ");
  Serial.println(device_id1, HEX);
  Serial.print("version: ");
  Serial.println(TURBIDOSTAT_VERSION);
  // Serial.print("device_id0: ");
  // Serial.println(device_id0, HEX);
  Serial.print("targetI: ");
  Serial.println(targetI);
  Serial.print("I0: ");
  Serial.println(I0);
  Serial.print("stirrerTargetSpeed: ");
  Serial.println(stirrerTargetSpeed);
  Serial.print("pumpDuration: ");
  Serial.println(pumpDuration);
  Serial.print("pumpInterval: ");
  Serial.println(pumpInterval);
  Serial.print("pumpMode: ");
  Serial.println(pumpMode);
  Serial.print("pumpPower: ");
  Serial.println(pumpPower);
  Serial.print("airpumpPower: ");
  Serial.println(airpumpPower);
  Serial.print("laserPower: ");
  Serial.println(laserPower);
}


///////////////
// COMMANDS
///////////////

void unknown_command(const char *command) {
  Serial.print("unknown command ");
  Serial.println(command);
}

// SLP - Set Laser Power
void setLaserPower(){
  char *arg = sCmd.next();
  if (arg != NULL) {
    int value = atoi(arg);
    laserPower = constrain(value, 0, 255);

    eeprom_write_block(&laserPower,     (void*)EEPROM_LASER_POWER + EEPROM_OFFSET,       sizeof(uint32_t));
    analogWrite(LASERPIN, laserPower);
    Serial.print("laserPower: ");
    Serial.println(laserPower);
  }
}

// SAP - Set Airpump Power
void setAirpumpPower(){
  char *arg = sCmd.next();
  if (arg != NULL) {
    airpumpPower = atoi(arg);  

    eeprom_write_block(&airpumpPower,     (void*)EEPROM_AIRPUMP_POWER + EEPROM_OFFSET,       sizeof(uint32_t));
    analogWrite(AIRPUMPPIN, airpumpPower);
    Serial.print("airpumpPower: ");
    Serial.println(airpumpPower);
  }
}

// SI0 - Set I0 ( intensity of clear solution )
void setI0(){
  I0 = I;
  eeprom_write_block(&I0,     (void*)EEPROM_I0 + EEPROM_OFFSET,       sizeof(uint32_t));
  targetI = I0*pow(10, -targetOD);
  Serial.print("I0: ");
  Serial.println(I0);
}

// SMP - Set Manual Pump
void setManualPump(){
  char *arg = sCmd.next();
  if (arg != NULL) {
    boolean isManualPumpOn = constrain( atoi(arg), 0, 1);
    if(isManualPumpOn){
      pumpOn(pumpPower);
      Serial.println("pump: on");
//    Serial.println(pumpPower);
    }
    else{
      analogWrite(PUMPPIN, 0);
      Serial.println("pump: off");
    }
  }
}

// SOD - Set Target Optical Density
void setOD(){
  char *arg = sCmd.next();
  if (arg != NULL) {
    targetOD = atof(arg);
    targetI = I0*pow(10, -targetOD);
    eeprom_write_block(&targetI,     (void*)EEPROM_TARGET_I + EEPROM_OFFSET,       sizeof(uint32_t));
    Serial.print("targetOD: ");
    Serial.println(targetOD);
    Serial.print("targetI: ");
    Serial.println(targetI);
  }
}

// SPD - Set Pump Duration
void setPumpDuration(){
  char *arg = sCmd.next();
  if (arg != NULL) {
    pumpDuration = atoi(arg); 
    eeprom_write_block(&pumpDuration,     (void*)EEPROM_PUMP_DURATION + EEPROM_OFFSET,       sizeof(uint32_t));        
    Serial.print("pumpDuration: ");
    Serial.println(pumpDuration);
  }
}

// SPM - Set Pump Mode (0=auto, 1=manual)
void setPumpMode(){
  char *arg = sCmd.next();
  if (arg != NULL) {
    pumpMode = atoi(arg);
    eeprom_write_block(&pumpMode,     (void*)EEPROM_PUMP_MODE + EEPROM_OFFSET,       sizeof(uint32_t));        
    Serial.print("pumpMode: ");
    Serial.println(pumpMode);
  }    
}

// SPP - Set Pump Power
void setPumpPower(){
  char *arg = sCmd.next();
  if (arg != NULL) {
    pumpPower = constrain(atoi(arg), 0, 255); 
    if(pumpMode == PUMP_MODE_MANUAL){ // 1 = manual
      pumpOn(pumpPower);
    }
    eeprom_write_block(&pumpPower,     (void*)EEPROM_PUMP_POWER + EEPROM_OFFSET,       sizeof(uint32_t));
    Serial.print("pumpPower: ");
    Serial.println(pumpPower);
  }
}

// SPW - Set Pump Interval
void setPumpInterval(){
  char *arg = sCmd.next();
  if (arg != NULL) {
    pumpInterval = atoi(arg); 
    eeprom_write_block(&pumpInterval,     (void*)EEPROM_PUMP_INTERVAL + EEPROM_OFFSET,       sizeof(uint32_t));
    Serial.print("pumpInterval: ");
    Serial.println(pumpInterval);
  }
}

// SDID - Set Serial Number
void setDeviceID(){ 
  char *arg1 = sCmd.next();
  char *arg2 = sCmd.next();
  if (arg1 && arg2) {
    uint32_t device_id1 = strtoul(arg1, NULL, 16);
    uint32_t device_id0 = strtoul(arg2, NULL, 16);
    Serial.print("deviceID: ");
    Serial.print(device_id0, HEX);
    Serial.print(", ");
    Serial.print(device_id1, HEX);
    Serial.println("");

    eeprom_write_block((const void*)&device_id0, (void*)EEPROM_SERIAL0 + EEPROM_OFFSET,  sizeof(device_id0));
    eeprom_write_block((const void*)&device_id1, (void*)EEPROM_SERIAL1 + EEPROM_OFFSET,  sizeof(device_id1));

    // check that it was written correctly
    uint32_t sera;
    uint32_t serb;
    eeprom_read_block((void*)&sera, (const void*)EEPROM_SERIAL0 + EEPROM_OFFSET, sizeof(sera));
    eeprom_read_block((void*)&serb, (const void*)EEPROM_SERIAL1 + EEPROM_OFFSET, sizeof(serb));

    Serial.print("deviceIdEeprom");
    Serial.println(sera, HEX);
    Serial.println(serb, HEX);
 }
}   

// SDN - set Device Name
void setDeviceName(){ 
  char delim[2] = "'";
  char *arg1 = sCmd.next(delim);
 
  if (arg1) {
    memcpy(device_name, arg1, 127);
    device_name[127] = 0;
    Serial.print("deviceName: ");
    Serial.println(device_name);

    eeprom_write_block((const void*)&device_name, (void*)EEPROM_DEVICE_NAME + EEPROM_OFFSET,  sizeof(device_name));
 }
}   

// SSS - Set Stirrer Speed
void setStirrerTargetSpeed(){
  char *arg = sCmd.next();
  if (arg != NULL) {
    stirrerTargetSpeed = atoi(arg); 
    
    eeprom_write_block(&stirrerTargetSpeed,     (void*)EEPROM_STIRRER_TARGET_SPEED + EEPROM_OFFSET,       sizeof(uint32_t));
    Serial.print("stirrerTargetSpeed: ");
    Serial.println(stirrerTargetSpeed);
  }
}

// ST - Set Time
void setTime(){   
  char *arg = sCmd.next();  
  if (arg != NULL) {
    uint32_t new_msecs = atol(arg);   
    msecs = new_msecs;
    Serial.print("ST: ");
    Serial.println(msecs);
  }
}  

// HALT - Stop all actuators
void halt(){   
  halted = true;

  pumpOff();
  airpumpOff();
  stirrerOff();

  Serial.println("halted");
}  


// RESET - reset the processor
void reset(){   
  Serial.print("resetting");
  void(* resetFunc) (void) = 0;
  resetFunc(); 
}  

///////////////////////////////////////////////////////////////////
void setPwmFrequency(int pin, int divisor) {
  byte mode;
  if(pin == 5 || pin == 6 || pin == 9 || pin == 10) {
    switch(divisor) {
      case 1: mode = 0x01; break;
      case 8: mode = 0x02; break;
      case 64: mode = 0x03; break;
      case 256: mode = 0x04; break;
      case 1024: mode = 0x05; break;
      default: return;
    }
    if(pin == 5 || pin == 6) {
      TCCR0B = TCCR0B & 0b11111000 | mode;
    } else {
      TCCR1B = TCCR1B & 0b11111000 | mode;
    }
  } else if(pin == 3 || pin == 11) {
    switch(divisor) {
      case    1: mode = 0x01; break;
      case    8: mode = 0x02; break;
      case   32: mode = 0x03; break;
      case   64: mode = 0x04; break;
      case  128: mode = 0x05; break;
      case  256: mode = 0x06; break;
      case 1024: mode = 0x07; break;
      default: return;
    }
    TCCR2B = TCCR2B & 0b11111000 | mode;
  }
}

//////////////////////////////////////////////////////////////////////
double getArduinoTemp(){
  // The internal temperature has to be used
  // with the internal reference of 1.1V.
  // Channel 8 can not be selected with
  // the analogRead function yet.

  // Set the internal reference and mux.
  ADMUX = (_BV(REFS1) | _BV(REFS0) | _BV(MUX3));
  ADCSRA |= _BV(ADEN);  // enable the ADC

  

  ADCSRA |= _BV(ADSC);  // Start the ADC

  delay(100);
  
  // Detect end-of-conversion
  while (bit_is_set(ADCSRA,ADSC));

  #define TEMP_OFFSET (7)
  #define AD2VOLTS          (1.1/1023.0) //1.1v=1023
  #define VOLTS2DEGCELSIUS  (25.0/0.314)
  
  // The returned temperature is in degrees Celcius.
  return ADCW * AD2VOLTS * VOLTS2DEGCELSIUS - TEMP_OFFSET;
}


void printData(){
  Serial.print("\tt="); 
  Serial.print(msecs);   
  Serial.print("\tI=");
  Serial.print((float)I, 4); 
  Serial.print("\tIa=");
  Serial.print((float)Ia/1000, 3);  
  Serial.print("\tIb=");
  Serial.print((float)Ib/1000, 3); 
  Serial.print("\tOD=");
  Serial.print(OD);  
  // Serial.print("\tlog10(I)=");
  // Serial.print(log10(I));
  // Serial.print("\tlog10(I0)=");
  // Serial.print(log10(I0));
  Serial.print("\tf_stirrer="); 
  Serial.print(60*1000000/(stirrerLastPeriod));  
  Serial.print("\ttemp="); 
  Serial.print((float)getArduinoTemp(), 2);     
  Serial.print("\tV_supply="); 
  //  U_ref R₂ / (R₁+R₂) = U_ref ⋅ 22kΩ / (10kΩ + 22kΩ) = U_ref ⋅ 22/32 = 2.5V  
  Serial.print( 1023.0 * 2.5 * 32.0 / (analogRead(VOLTAGEPIN) * 22.0), 3);     
  // Serial.print((float)map(analogRead(VOLTAGEPIN), 0, 1023, 0, 5));     
  Serial.println("");
}

// Serial command callbacks
void initSerialCommands(){
  sCmd.addCommand("getSettings", printSettings); 
  sCmd.addCommand("GS", printSettings); 
  sCmd.addCommand("gs", printSettings); 
  sCmd.addCommand("ls", printSettings); 

  sCmd.addCommand("setDeviceName", setDeviceName); 
  sCmd.addCommand("SDN", setDeviceName); 
  sCmd.addCommand("sdn", setDeviceName); 

  sCmd.addCommand("setAirpumpPower", setAirpumpPower);
  sCmd.addCommand("SAP", setAirpumpPower); 
  sCmd.addCommand("sap", setAirpumpPower);

  sCmd.addCommand("setI0", setI0); 
  sCmd.addCommand("SI0", setI0); 
  sCmd.addCommand("si0", setI0); 

  sCmd.addCommand("setManualPump", setManualPump); 
  sCmd.addCommand("SMP", setManualPump); 
  sCmd.addCommand("smp", setManualPump); 

  sCmd.addCommand("setOD", setOD); 
  sCmd.addCommand("SOD", setOD); 
  sCmd.addCommand("sod", setOD); 

  sCmd.addCommand("setPumpDuration", setPumpDuration); 
  sCmd.addCommand("SPD", setPumpDuration); 
  sCmd.addCommand("spd", setPumpDuration); 

  sCmd.addCommand("setPumpMode", setPumpMode); 
  sCmd.addCommand("SPM", setPumpMode); 
  sCmd.addCommand("spm", setPumpMode); 

  sCmd.addCommand("setPumpPower", setPumpPower); 
  sCmd.addCommand("SPP", setPumpPower); 
  sCmd.addCommand("spp", setPumpPower); 

  sCmd.addCommand("setPumpInterval", setPumpInterval); 
  sCmd.addCommand("SPW", setPumpInterval); 
  sCmd.addCommand("spw", setPumpInterval); 

  sCmd.addCommand("setStirrerTargetSpeed", setStirrerTargetSpeed); 
  sCmd.addCommand("SSS", setStirrerTargetSpeed); 
  sCmd.addCommand("sss", setStirrerTargetSpeed); 

  sCmd.addCommand("setLaserPower", setLaserPower); 
  sCmd.addCommand("SLP", setLaserPower); 
  sCmd.addCommand("slp", setLaserPower);

  sCmd.addCommand("setTime", setTime); 
  sCmd.addCommand("ST", setTime); 
  sCmd.addCommand("st", setTime); 

  sCmd.addCommand("setDeviceID", setDeviceID); 
  sCmd.addCommand("SDID", setDeviceID); 
  sCmd.addCommand("sdid", setDeviceID); 

  sCmd.addCommand("HALT", halt); 
  sCmd.addCommand("halt", halt); 

  sCmd.addCommand("RESET", reset); 
  sCmd.addCommand("reset", reset); 
  sCmd.setDefaultHandler(unknown_command);    
}

// class variable{
//   void *p = NULL;

// }
// void pointerTest(uint32_t &var){
//   char s[32];
//   sprintf(s, "(%p):", &var);
//   Serial.print(s);
//   Serial.println(var);
// }

// void pointerTest(float &var){
//   char s[32];
//   sprintf(s, "(%p):", &var);
//   Serial.print(s);
//   Serial.println(var);
// }

///////////////////////////////////////////////////////////////////
//
// SETUP
//
///////////////////////////////////////////////////////////////////
void setup() 
{
  eeprom_load();
  
  pinMode(LEDPIN, OUTPUT); 
  digitalWrite(LEDPIN, LOW);

  // sensors  
  pinMode(SENSOR_A_PIN, INPUT_PULLUP);
  attachInterrupt(0, isrSensorA, RISING);

  pinMode(SENSOR_B_PIN, INPUT_PULLUP);
  attachInterrupt(1, isrSensorB, RISING);  

  pinMode(VOLTAGEPIN, INPUT);
  
  // medium pump
  pinMode(PUMPPIN, OUTPUT); 
  pumpOff();
  // air pump
  pinMode(AIRPUMPPIN, OUTPUT); 
  airpumpOff();
  // stirrer
  pinMode(HALLPIN, INPUT_PULLUP);
  PCintPort::attachInterrupt(HALLPIN, &isr_hall_sensor, FALLING); 
  pinMode(STIRRERPIN, OUTPUT); 
  analogWrite(STIRRERPIN, stirrerOut);


  setPwmFrequency(STIRRERPIN, PWM_DEVISOR);  
  setPwmFrequency(AIRPUMPPIN, PWM_DEVISOR);
  
  Timer2init();


  // laser
  // laserPower = 125;
  analogWrite(LASERPIN, laserPower); 


  Serial.begin(115200);

  initSerialCommands();


  Serial.println("START");
  Serial.println("Turbidostat");

  printSettings();

  // pointerTest(pumpInterval);////////////////////////////////////////7
}

///////////////////////////////////////////////////////////////////
//
// MAIN LOOP
//
///////////////////////////////////////////////////////////////////
void loop(){
  sCmd.readSerial();
  
  if(!halted){
    if (msecs % 1000 == 0){
      // light sensors
      uint32_t na = cnta;
      uint32_t nb = cntb;
      Ia = na*10;
      Ib = nb*10;
      I  = Ia*1000.0/Ib;
      OD = -(log10(I)-log10(I0));

      printData();

      // reset sensor counter
      cnta = 0;
      cntb = 0;

      laser_control();    
    }

    ////////////////////////
    // control 
    ////////////////////////

    // stirrer
    int32_t _lastInterruptTime = now - stirrerLastTime;  // time since last interrupt
    if(1e6 < _lastInterruptTime){  // restart stirrer if stopped for more than a second
      run_stirrer_control = true;
      stirrerLastPeriod = _lastInterruptTime;
    }
    if(run_stirrer_control){
      stirrer_control();
      run_stirrer_control = false;
    }
    
    // Pump
    if((targetI != 0) && (pumpMode == PUMP_MODE_AUTOMATIC)){
      static uint32_t lastPulsTime = 0;
      static boolean pumppin = false;
      
      // hello future me, please comment and find meaningful names
      if( targetI > I ){        
        if((pumppin == false) && (lastPulsTime + pumpInterval < msecs)){
          thresholdCnt++;
          if(thresholdCnt >= NTIMESTHRESHOLD){
            thresholdCnt = NTIMESTHRESHOLD; // to prevent overflow
            pumpOn(pumpPower);
            pumppin = true;
            lastPulsTime = msecs;
            Serial.println("pump: on");
          }        
        }
      } 
      else{
        thresholdCnt = 0;
      }
      if( (pumppin == true) && (lastPulsTime + pumpDuration < msecs)){
        
        pumpOff();
        pumppin = false;
        Serial.println("pump: off");
      }    
    }
  }
}

// END OF FILE
