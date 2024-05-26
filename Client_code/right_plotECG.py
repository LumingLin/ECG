import asyncio
import csv
import time
import sys
from PyQt5 import QtWidgets
import pyqtgraph as pg
from bleak import BleakClient
from qasync import QEventLoop
from collections import deque

# Define the window length and the BLE device address
length_window = 200  # Number of data points to display on the graph

ECG_CHAR_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
address = "0F1540B9-C0D1-D5B1-D801-58F1BF8FD51B"  # ESP32 BLE UUID

class Window(pg.GraphicsLayoutWidget):
    def __init__(self, loop=None, parent=None):
        super().__init__(parent)
        self._loop = loop

        self.setWindowTitle("ECG Data Plot")
        plot = self.addPlot(title="ECG Signal")
        plot.setYRange(0, 1023, padding=0)  # Adjust range according to expected ECG signal amplitude

        self._ecg_data = deque([0] * length_window)
        self._curve = plot.plot(self._ecg_data, pen='r', name='ECG')
        self._client = BleakClient(address, loop=self._loop)

    # Ensure other methods and properties are correctly implemented here...


    @property
    def client(self):
        return self._client
    
    async def connect(self):
        # Scan for devices and connect
        address = await self.find_device_by_name(DEVICE_NAME)
        if address:
            await self.connect_and_listen(address)
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
        # print(f"Received ECG value: {ecg_value}")
        self.update_plot(ecg_value)

    def update_plot(self, ecg_value):
        self._ecg_data.append(ecg_value)
        self._ecg_data.popleft()
        self._curve.setData(self._ecg_data)

    def closeEvent(self, event):
        asyncio.ensure_future(self.stop(), loop=self._loop)
        super().closeEvent(event)



def main(args):
    app = QtWidgets.QApplication(args)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = Window(loop=loop)
    window.show()

    with loop:
        asyncio.ensure_future(window.start(), loop=loop)
        loop.run_forever()

if __name__ == "__main__":
    main(sys.argv)