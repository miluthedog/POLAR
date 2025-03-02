import serial
import time
import intelhex

class GRBL:
    def __init__(self, port, baud):
        self.PORT = port                                    # Left USB = COM 5
        self.BAUD = baud                                    # 115200
        self.HEX_FILE = "modules/firmwareConvert/grbl.hex"  # .hex
        self.PAGE_SIZE = 128                                # Flash page size for ATmega328P (Uno)
        self.connection = None

    def checkFirmware(self):
        try:
            self.connection = serial.Serial(self.PORT, self.BAUD, timeout=1)
            time.sleep(2)
            self.connection.flushInput()

            self.connection.write(b"\r\n")  # Request GRBL
            time.sleep(0.1)
            response = self.connection.read_until(b"\n").decode().strip()

            if "ok" in response:
                return True
            else:
                print("No firmware detected")
                return False
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            return False
        finally:
            if self.connection and self.connection.is_open:
                self.connection.close()

    def reset(self):
        try:
            self.connection = serial.Serial(self.PORT, 1200)
            time.sleep(0.1)
            self.connection.close()
            time.sleep(2)
        except serial.SerialException as e:
            print(f"Reset error: {e}")

    def syncBootloader(self):
        if not self.connection or not self.connection.is_open:
            print("Error: no connection")
            return False
        SYNC = b'\x30'
        CRC_EOP = b'\x20'
        for _ in range(5):
            self.connection.write(SYNC + CRC_EOP)
            time.sleep(0.1)
            resp = self.connection.read(2)
            if resp == b'\x14\x10':
                return True
        print("Error: Failed to sync with bootloader")
        return False

    def uploadHex(self):
        try:
            ih = intelhex.IntelHex()                        # initial ih
            ih.fromfile(self.HEX_FILE, format='hex')        # load .hex
            bin_data = ih.tobinstr()                        # .hex to binary
            print(f"Firmware size: {len(bin_data)} bytes")   

            self.reset()
            try:
                self.connection = serial.Serial(self.PORT, self.BAUD, timeout=1)
            except serial.SerialException as e:
                print(f"Serial connection error: {e}")
                return

            if not self.syncBootloader():
                self.connection.close()
                return

            STK_LOAD_ADDRESS = b'\x55' 
            STK_PROG_PAGE = b'\x64'
            STK_INSYNC = b'\x14'
            STK_OK = b'\x10'
            CRC_EOP = b'\x20'

            for addr in range(0, len(bin_data), self.PAGE_SIZE):
                chunk = bin_data[addr:addr + self.PAGE_SIZE]
                chunk_len = len(chunk)
                if chunk_len == 0:
                    break

                if chunk_len < self.PAGE_SIZE:
                    chunk += b'\xFF' * (self.PAGE_SIZE - chunk_len)

                addr_words = addr // 2
                addr_bytes = bytes([addr_words & 0xFF, (addr_words >> 8) & 0xFF])
                self.connection.write(STK_LOAD_ADDRESS + addr_bytes + CRC_EOP)
                if self.connection.read(2) != STK_INSYNC + STK_OK:
                    print(f"Address {addr} failed")
                    break

                size_bytes = bytes([0x00, self.PAGE_SIZE & 0xFF]) 
                self.connection.write(STK_PROG_PAGE + size_bytes + b'\x46' + chunk + CRC_EOP)
                resp = self.connection.read(2)
                if resp == STK_INSYNC + STK_OK:
                    print(f"Uploaded page at address {addr}")
                else:
                    print(f"Error: failed at {addr}: {resp.hex()}")
                    break

            print("Upload complete!")
            self.connection.close()

        except Exception as e:
            print(f"Error: {e}")
