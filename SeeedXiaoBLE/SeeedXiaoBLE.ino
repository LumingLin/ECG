#include <bluefruit.h>

BLEService ecgService("12345678-1234-5678-1234-56789abcdef0"); // Custom service UUID
BLECharacteristic ecgChar("beb5483e-36e1-4688-b7f5-ea07361b26a8"); // Custom characteristic UUID

void setup() {
  Bluefruit.begin();
  Bluefruit.setName("SEEED_ECG");

  ecgService.begin();
  ecgChar.setProperties(CHR_PROPS_NOTIFY);
  ecgChar.setPermission(SECMODE_OPEN, SECMODE_NO_ACCESS);
  ecgChar.setFixedLen(4);
  ecgChar.begin();

  startAdvertising();
  Bluefruit.autoConnLed(true);
  Bluefruit.setConnLedInterval(250);

  Bluefruit.Periph.setConnectCallback(connect_callback);
  Bluefruit.Periph.setDisconnectCallback(disconnect_callback);
}

void startAdvertising() {
  Bluefruit.Advertising.addService(ecgService);
  Bluefruit.Advertising.addName();
  Bluefruit.Advertising.restartOnDisconnect(false); // Changed to false to control manually
  Bluefruit.Advertising.start(0); // Start advertising without a timeout
}

void connect_callback(uint16_t conn_handle) {
  Bluefruit.Advertising.stop(); // Stop advertising once connected
}

void disconnect_callback(uint16_t conn_handle, uint8_t reason) {
  startAdvertising(); // Start advertising again after disconnect
}

void loop() {
  static unsigned long lastTime = 0;
  static unsigned long lastPrintTime = 0;
  static int dataCount = 0;

  unsigned long currentTime = millis();

  if (currentTime - lastTime > 5) { // Update every 5 ms (~200 Hz sampling rate)
    int ecgValue = analogRead(0);
    ecgChar.notify(&ecgValue, sizeof(ecgValue));
    lastTime = currentTime;
    dataCount += sizeof(ecgValue);
  }

  if (currentTime - lastPrintTime > 1000) { // Every 1000 ms print data rate
    Serial.print("Data rate: ");
    Serial.print(dataCount);
    Serial.println(" bytes per second");
    lastPrintTime = currentTime;
    dataCount = 0; // Reset count after printing
  }
}
