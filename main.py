from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QPushButton, QLabel, QSizePolicy, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from modules.camera import camera
from modules.connect import Arduino
from modules.firmware import GRBL
from modules.imageConvert import png2gcode

class polarUI(QWidget):
# =============== FRONT END ===============

    def __init__(self):
        super().__init__()
        self.resize(1270, 720)
        self.setWindowTitle("POLAR")
        self.setWindowIcon(QIcon("polar.ico"))
        self.connection = None

    # ========== Left Widget ==========

            # Left: combo boxes
        leftCombos = QHBoxLayout()
        self.combo1 = QComboBox()
        self.combo2 = QComboBox()
        for combo in [self.combo1]:
            combo.addItems(["COM5", "COM4", "COM3", "COM2", "COM1"])
        self.combo2.addItem("115200")
        leftCombos.addWidget(self.combo1)
        leftCombos.addWidget(self.combo2)
            # Left: buttons
        leftButtons = QHBoxLayout()
        self.button1 = QPushButton("Firmware: OFF")
        self.button2 = QPushButton("Camera: OFF")
        self.button3 = QPushButton("OFF")
        self.button1.setFixedSize(90, 30)
        self.button2.setFixedSize(90, 30)
        self.button3.setFixedSize(30, 30)
        self.button1.clicked.connect(self.firmware)
        self.button2.clicked.connect(self.camera)
        self.button3.clicked.connect(self.connect)
        leftButtons.addWidget(self.button1)
        leftButtons.addWidget(self.button2)
        leftButtons.addWidget(self.button3)
            # Left: area
        self.leftArea = QTextEdit()
        self.leftArea.setReadOnly(True)
        self.leftArea.setStyleSheet("background-color: #222831; color: #eeeeee; font-size: 12px; border: 1px solid #00adb5;")
        self.leftArea.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.responses = []
            # Left: 3x3 joystick
        leftJoystick = QGridLayout()
        self.joystick = []
        joystickLabels =  [["NW", "N", "NE"],
                            ["W", "🏠", "E"],
                            ["SW", "S", "SE"]]
        for row in range(3):
            for col in range(3):
                button = QPushButton(joystickLabels[row][col])
                button.setFixedSize(60, 60)
                self.joystick.append(button)
                leftJoystick.addWidget(button, row, col)
        for button in self.joystick:
            button.clicked.connect(self.moving)
            # ===== Left Widget =====
        left = QVBoxLayout()
        left.addLayout(leftCombos)
        left.addLayout(leftButtons)
        left.addWidget(self.leftArea)
        left.addLayout(leftJoystick)
        leftWidget = QWidget()
        leftWidget.setLayout(left)
        leftWidget.setFixedWidth(240)
        leftWidget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

    # ========== Right Widget ==========  

            # Right-down: button 
        self.buttonBig = QPushButton("Bottom Button")
        self.buttonBig.setFixedSize(150, 40)
        self.buttonBig.clicked.connect(self.imageConvert)
            # Right-down Widget = button + ...
        rightdown = QVBoxLayout()
        rightdown.addWidget(self.buttonBig, alignment=Qt.AlignmentFlag.AlignCenter)
        RightdownWidget = QWidget()
        RightdownWidget.setLayout(rightdown)
        RightdownWidget.setFixedHeight(100)
        RightdownWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            # Right-top area
        self.RighttopArea = QLabel()
        self.RighttopArea.setStyleSheet("background-color: white; border: 1px solid black;")
        self.RighttopArea.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            # ===== Right Widget =====
        right = QVBoxLayout()
        right.addWidget(self.RighttopArea)
        right.addWidget(RightdownWidget)
        rightWidget = QWidget()
        rightWidget.setLayout(right)

    # ========== Main ==========

        main = QHBoxLayout()
        main.addWidget(leftWidget)
        main.addWidget(rightWidget)
        self.setLayout(main)

# =============== BACK END ===============

    def firmware(self):
        firmware = GRBL(self.combo1.currentText(), self.combo2.currentText())
        alreadyGrbl = firmware.checkFirmware()
        if not alreadyGrbl:
            response = "Uploading firmware..."
            firmware.uploadHex()
            self.responses.append(response)
        self.button1.setText("Firmware: ON")
        response = "Firmware: ready"
        self.responses.append(response)
        self.leftArea.setText("<br>".join(self.responses)) 

    def camera(self):
        print("upcoming")

    def connect(self):
        connector = Arduino(self.combo1.currentText(), self.combo2.currentText())
        if self.button3.text() == "OFF":
            self.connection, response = connector.connect(self.connection)
            if self.connection:
                self.button3.setText("ON")
        else:
            self.connection, response = connector.disconnect(self.connection)
            if not self.connection:
                self.button3.setText("OFF")

        self.responses.append(response)
        self.leftArea.setText("<br>".join(self.responses))

    def moving(self):
        print("hi")

    def imageConvert(self):
        print("hi")

if __name__ == "__main__":
    app = QApplication([])
    window = polarUI()
    window.show()
    app.exec()
