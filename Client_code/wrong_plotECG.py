import asyncio
from bleak import BleakClient, BleakScanner
from pyqtgraph.Qt import QtWidgets, QtCore
import pyqtgraph as pg
from collections import deque

# Constants
DEVICE_NAME = "ESP32_ECG"
ECG_CHAR_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"


class ECGPlotter:
    def __init__(self):
        # Set up the application window
        self.app = QtWidgets.QApplication([])
        self.win = pg.GraphicsLayoutWidget(show=True, title="Live ECG Plot")
        self.plot = self.win.addPlot(title="ECG Signal")
        self.plot.setYRange(0, 3.3, padding=0)  # Set the Y range of ECG voltage
        self.curve = self.plot.plot(pen='y')
        self.data = deque(maxlen=200)  # Define a fixed-length deque to store data

    def update_plot(self, ecg_value):
        # Append new data and update the plot
        self.data.append(ecg_value)
        self.curve.setData(list(self.data))
    
    async def run(self):
        # Scan for devices and connect
        address = await self.find_device_by_name(DEVICE_NAME)
        if address:
            await self.connect_and_listen(address)
        else:
            print("ECG device not found. Please ensure the device is on and advertising.")

    async def find_device_by_name(self, name):
        # Scan for BLE devices and filter by name
        devices = await BleakScanner.discover()
        for device in devices:
            if device.name == name:
                print(f"Found device: {device.name} at {device.address}")
                return device.address
        return None

    async def connect_and_listen(self, address):
        async with BleakClient(address) as client:
            if client.is_connected:
                print(f"Connected to {address}")
                services = await client.get_services()
                print("Services and characteristics found:")
                for service in services:
                    print(service)
                    for char in service.characteristics:
                        print(char)
                await client.start_notify(ECG_CHAR_UUID, self.notification_handler)
                await asyncio.sleep(30)  # Keep listening for 30 seconds
                await client.stop_notify(ECG_CHAR_UUID)
            else:
                print("Failed to connect.")


    def notification_handler(self, sender, data):
        # Process incoming data
        ecg_value = int.from_bytes(data, byteorder='little', signed=False) / 4095.0 * 3.3
        print(f"Received ECG value: {ecg_value}")
        QtCore.QMetaObject.invokeMethod(self, "update_plot", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(float, ecg_value))


if __name__ == "__main__":
    asyncio.run(ECGPlotter().run())

