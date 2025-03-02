import serial
import time

class Arduino:
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
        
    def send(self, connection, data):
        if not connection:
            return "Error: no connection"
        try:
            connection.write(f"{data}\n".encode('utf-8'))
            time.sleep(0.1)
            while connection.in_waiting > 0:
                sentData = connection.readline().decode('utf-8').strip()
                return (sentData)
        except serial.SerialException as error:
            return (f"Failed to connect: {error}")