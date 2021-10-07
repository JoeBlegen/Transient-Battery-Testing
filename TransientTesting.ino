#define RESISTANCE 0.4  // Resistance used

int voltagePin = A0;    // Pin for voltage output
int relayPin = 3;      // Pin that controls relay

bool relayState = 0;  // State of relay (0=Open, 1=Closed)
bool ledState = 0;  //  State of LED (0=Off, 1=On)

bool stopFlag = 0;  // Stops test when minimmum battery voltage is reached

int voltageValue = 0;  // Stores voltage coming from battery
float batteryVoltageNormalized = 4.2; // Stores battery voltage after normalizing from Arduino
float current = 0.0;  // Current coming from battery (batteryVoltageNormalized / RESISTANCE)
float minBatteryVoltage = 0;  //  Battery voltage to stop test at
float restTime = 5.0; // Time that relay remains closed (Seconds)
float activeTime = 5.0; // Time that relay remains open for (Seconds)

unsigned long previousMillis = 0; // Stores previous time value
unsigned long currentMillis = 0; // Stores current time value
double timeInState = 0; // Stores total time switch has spent open/closed
double totalTime = 0; // Stores total time test has spent running

void setup() {
  // Set digital led and relay pins to output
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(relayPin, OUTPUT);
  Serial.begin(9600);

  // Headings
  Serial.print("Timestamp (s), Discharge Current (A), Battery Voltage (V) \n");
  delay(100);
}

void loop() {
  if (stopFlag == 0) {
    delay(150);
    previousMillis = currentMillis;
    currentMillis = millis();
    // Tracks relay time spent open/closed and total time test has been running
    timeInState += (currentMillis-previousMillis);
    totalTime += (currentMillis-previousMillis);
    // If the relay has been open/closed for more than wanted time, switch state
    if(relayState == 1 && timeInState >= (activeTime*1000)) {
      timeInState = 0;
      relayState = 0;
      digitalWrite(relayPin, relayState); //Close relay
    } else if(relayState == 0 && timeInState >= (restTime*1000)) {
      timeInState = 0;
      relayState = 1;
      digitalWrite(relayPin, relayState);  //Open relay
    }

    // Reads pin for voltage
    voltageValue = analogRead(voltagePin);

    // Normalized adc
    batteryVoltageNormalized = voltageValue * (5.0 / 1023.0);

    // Battery Voltage is never 0 when closed
    if (relayState == 0){
      batteryVoltageNormalized = 0;
    }
    current = (batteryVoltageNormalized / RESISTANCE);

    Serial.print(totalTime/1000);
    Serial.print(",");
    Serial.print(current);
    Serial.print(",");
    Serial.print(batteryVoltageNormalized);
    Serial.print("\n");

    // Stop test if battery is under certain voltage
    if(batteryVoltageNormalized < minBatteryVoltage) {
      stopFlag = 1;
    }

    // Blink LED
    ledState = !ledState;
    digitalWrite(LED_BUILTIN, ledState);
  } else if(stopFlag == 1) {
    relayState = 0;
    digitalWrite(relayPin, 0); // Open relay
    digitalWrite(LED_BUILTIN, HIGH); // Turn on LED to signal stop
    while(true){  // Stay here until Arduino is reset
      delay(1000);
    }
  }
}
