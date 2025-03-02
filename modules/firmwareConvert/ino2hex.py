import subprocess
import os

ARDUINO_CLI_PATH = r"D:/arduino-cli_1.2.0_Windows_64bit/arduino-cli.exe"
BOARD_FQBN = "arduino:avr:uno"
SKETCH_PATH = r"D:/Pha hust/Projects/project 4 axis laser engrave/code/software/modeles/firmwareConvert/grbl"
OUTPUT_HEX = r"D:/Pha hust/Projects/project 4 axis laser engrave/code/software/grbl.hex"

def compile_sketch():
    try:
        print(" Compiling Arduino sketch...")
        cmd = [
            ARDUINO_CLI_PATH, "compile",
            "--fqbn", BOARD_FQBN,
            "--output-dir", "./output",
            SKETCH_PATH
        ]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Compilation successful!")
        return True
    except subprocess.CalledProcessError as e:
        print("Compilation failed!")
        print(e.stderr)
        return False

def find_hex():
    hex_files = [f for f in os.listdir("./output") if f.endswith(".hex")]
    if hex_files:
        hex_path = os.path.join("./output", hex_files[0])
        os.rename(hex_path, OUTPUT_HEX)
        print(f"HEX file saved as: {OUTPUT_HEX}")
        return True
    else:
        print("No HEX file found!")
        return False

if compile_sketch():
    find_hex()
