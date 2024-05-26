//still has error when vscode try to detect it
/*
 Task exception was never retrieved
future: <Task finished name='Task-1' coro=<Window.connect() done, defined at /Users/vincentlin/Desktop/Research2/AD8232/plotECG.py:43> exception=BleakError('Failed to update the notification status for characteristic 41: Error Domain=CBATTErrorDomain Code=10 "The attribute could not be found." UserInfo={NSLocalizedDescription=The attribute could not be found.}')>
Traceback (most recent call last):
  File "/Users/vincentlin/Desktop/Research2/AD8232/plotECG.py", line 47, in connect
    await self.start()
  File "/Users/vincentlin/Desktop/Research2/AD8232/plotECG.py", line 53, in start
    await self.client.start_notify(ECG_CHAR_UUID, self.notification_handler)
  File "/opt/homebrew/lib/python3.12/site-packages/bleak/__init__.py", line 844, in start_notify
    await self._backend.start_notify(characteristic, wrapped_callback, **kwargs)
  File "/opt/homebrew/lib/python3.12/site-packages/bleak/backends/corebluetooth/client.py", line 364, in start_notify
    await self._delegate.start_notifications(characteristic.obj, callback)
  File "/opt/homebrew/lib/python3.12/site-packages/bleak/backends/corebluetooth/PeripheralDelegate.py", line 230, in start_notifications
    await future
bleak.exc.BleakError: Failed to update the notification status for characteristic 41: Error Domain=CBATTErrorDomain Code=10 "The attribute could not be found." UserInfo={NSLocalizedDescription=The attribute could not be found.}
Trace/BPT trap: 5
 */


#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>

// UUIDs for BLE service and characteristic
#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

BLEServer *pServer = NULL;
BLECharacteristic *pCharacteristic = NULL;

void setup() {
  Serial.begin(115200); // Start serial communication
  BLEDevice::init("ESP32_ECG"); // Initialize the BLE device

  // Create the BLE Server
  pServer = BLEDevice::createServer();
  
  // Create the BLE Service
  BLEService *pService = pServer->createService(SERVICE_UUID);

  // Create a BLE Characteristic with properties for read, write, and notify
  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_READ |
                      BLECharacteristic::PROPERTY_WRITE |
                      BLECharacteristic::PROPERTY_NOTIFY
                    );

  // Set the initial value for the characteristic
  int initialValue = 0;
  pCharacteristic->setValue((uint8_t*)&initialValue, sizeof(initialValue));

  // Start the service
  pService->start();

  // Start advertising the service
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);  // Recommended for iPhone connectivity
  pAdvertising->setMinPreferred(0x12);
  BLEDevice::startAdvertising();
  Serial.println("Waiting for a client connection to notify...");
}

void loop() {
  static uint32_t lastTime = 0; // to control data rate

  // Check if a client is connected to the server
  if (pServer->getConnectedCount() > 0) {
    uint32_t currentTime = millis();
    if (currentTime - lastTime > 10) { // update every 10 ms (~100 Hz sampling rate)
      int ecgValue = analogRead(A0); // Read ECG value from analog pin A0
      pCharacteristic->setValue((uint8_t*)&ecgValue, sizeof(ecgValue));
      pCharacteristic->notify(); // Notify connected client
      lastTime = currentTime;
    }
  }
  delay(5); // Slight delay to stabilize the loop
}
