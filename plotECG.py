import asyncio
import sys
from PyQt5 import QtWidgets
import pyqtgraph as pg
from bleak import BleakClient, BleakScanner
from qasync import QEventLoop
from collections import deque
import time

# Define the window length and the BLE device name
length_window = 200  # Number of data points to display on the graph
DEVICE_NAME = "SEEED_ECG"
ECG_CHAR_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

class Window(pg.GraphicsLayoutWidget):
    def __init__(self, loop=None, parent=None):
        super().__init__(parent)
        self._loop = loop
        self.setWindowTitle("ECG Data Plot")
        plot = self.addPlot(title="ECG Signal")
        plot.setYRange(0, 1023, padding=0)
        self._ecg_data = deque([0] * length_window)
        self._curve = plot.plot(self._ecg_data, pen='r', name='ECG')
        self._client = None
        self.last_time = time.time()
        self.data_received = 0

    @property
    def client(self):
        return self._client

    async def find_device_by_name(self):
        print("Scanning for devices...")
        devices = await BleakScanner.discover(timeout=3.0)  # Extended scanning duration
        for device in devices:
            print(f"Scanned Device: {device.name} at {device.address}")
            if device.name and DEVICE_NAME in device.name:
                print(f"Found device: {device.name} at {device.address}")
                return device.address
        print("No matching device found.")
        return None

    async def connect(self):
        address = await self.find_device_by_name()
        if address:
            self._client = BleakClient(address, loop=self._loop)
            await self.start()
        else:
            print("ECG device not found. Please ensure the device is on and advertising.")

    async def start(self):
        await self.client.connect()
        await self.client.start_notify(ECG_CHAR_UUID, self.notification_handler)
        print("Started monitoring ECG...")

    async def stop(self):
        await self.client.stop_notify(ECG_CHAR_UUID)
        await self.client.disconnect()

    def notification_handler(self, sender, data):
        ecg_value = int.from_bytes(data, byteorder='little')
        self.update_plot(ecg_value)
        self.data_received += len(data)
        current_time = time.time()
        if current_time - self.last_time >= 1.0:
            print(f"Data rate: {self.data_received} bytes/sec")
            self.last_time = current_time
            self.data_received = 0

    def update_plot(self, ecg_value):
        self._ecg_data.append(ecg_value)
        self._ecg_data.popleft()
        self._curve.setData(self._ecg_data)

    def closeEvent(self, event):
        if self.client:
            asyncio.ensure_future(self.stop(), loop=self._loop)
        super().closeEvent(event)

def main(args):
    app = QtWidgets.QApplication(args)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = Window(loop=loop)
    window.show()

    with loop:
        asyncio.ensure_future(window.connect(), loop=loop)
        loop.run_forever()

if __name__ == "__main__":
    main(sys.argv)
