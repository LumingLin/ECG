import serial
import csv
import time

# Setup serial connection (adjust COM port as needed)
ser = serial.Serial('/dev/tty.usbserial-0001', 115200)  # Open serial port that Arduino is using

# Open a CSV file to store the data
with open('ecg_data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "ECG Value"])  # Write CSV header

    while True:
        try:
            line = ser.readline().decode().strip()  # Read a line from the serial port
            if line:  # If line is not empty
                timestamp, value = line.split(',')  # Split the line into parts
                writer.writerow([timestamp, value])  # Write to CSV
        except KeyboardInterrupt:
            print("Finished recording.")
            break
        except ValueError:
            continue  # If there is a malformed line, ignore it

ser.close()  # Close serial port
