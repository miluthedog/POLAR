import serial
import time

class Connection:
    def __init__(self, port, baud):
        self.PORT = port
        self.BAUD = baud

    def connect(self, connection):
        try:
            connection = serial.Serial(self.PORT, self.BAUD, timeout=1)
            time.sleep(2)
            connection.reset_input_buffer()
            return connection, (f"Connected: {self.PORT} & {self.BAUD}")
        except serial.SerialException as error:
            connection = None
            return connection, (f"Error: {error}")

    def disconnect(self, connection):
        if connection:
            connection.close()
            return None, "Disconnected"
        return connection, "Error: no connection"

class Communication:
    def __init__(self, connection):
        self.connection = connection

    def send(self, data):
        self.connection.write(f"{data}\n".encode('utf-8'))
        time.sleep(0.1)
        while self.connection.in_waiting > 0:
            sentData = self.connection.readline().decode('utf-8').strip()
            return sentData
