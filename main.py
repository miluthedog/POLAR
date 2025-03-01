from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QPushButton, QLabel, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class polarUI(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1270, 720)
        self.setWindowTitle("POLAR")
        self.setWindowIcon(QIcon("polar.ico"))

    # ========== Left Widget ==========

            # Left: combo boxes
        leftCombos = QHBoxLayout()
        self.combo1 = QComboBox()
        self.combo2 = QComboBox()
        for combo in [self.combo1]:
            combo.addItems(["COM3", "COM4", "COM5"])
        self.combo2.addItem("115200")
        leftCombos.addWidget(self.combo1, alignment=Qt.AlignmentFlag.AlignTop)
        leftCombos.addWidget(self.combo2, alignment=Qt.AlignmentFlag.AlignTop)
            # Left: buttons
        leftButtons = QVBoxLayout()
        self.button1 = QPushButton("Button 1")
        self.button2 = QPushButton("Button 2")
        self.button1.setFixedSize(120, 30)
        self.button2.setFixedSize(120, 30)
        leftButtons.addWidget(self.button1)
        leftButtons.addWidget(self.button2)
            # Left: 3x3 joystick
        leftJoystick = QGridLayout()
        self.joystick_buttons = []
        joystick_labels =  [["NW", "N", "NE"],
                            ["W", "🏠", "E"],
                            ["SW", "S", "SE"]]
        for row in range(3):
            for col in range(3):
                button = QPushButton(joystick_labels[row][col])
                button.setFixedSize(50, 50)
                self.joystick_buttons.append(button)
                leftJoystick.addWidget(button, row, col)
            # Left Widget = combo boxes + buttons + 3x3 joystick (downward)
        left = QVBoxLayout()
        left.addLayout(leftCombos)
        left.addLayout(leftButtons)
        left.addLayout(leftJoystick)
        leftWidget = QWidget()
        leftWidget.setLayout(left)
        leftWidget.setFixedWidth(200)
        leftWidget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

    # ========== Right Widget ==========  

            # Right-down: button 
        self.big_button = QPushButton("Bottom Button")
        self.big_button.setFixedSize(150, 40)
            # Right-down Widget = button + ...
        rightdown = QVBoxLayout()
        rightdown.addWidget(self.big_button, alignment=Qt.AlignmentFlag.AlignCenter)
        RightdownWidget = QWidget()
        RightdownWidget.setLayout(rightdown)
        RightdownWidget.setFixedHeight(100)
        RightdownWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            # Right-top Widget (area)
        self.RighttopWidget = QLabel()
        self.RighttopWidget.setStyleSheet("background-color: white; border: 1px solid black;")
        self.RighttopWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            # Right Widget = Right-down Widget + Right-top Widget
        right = QVBoxLayout()
        right.addWidget(self.RighttopWidget)
        right.addWidget(RightdownWidget)
        rightWidget = QWidget()
        rightWidget.setLayout(right)

    # ========== Main ==========

        main = QHBoxLayout()
        main.addWidget(leftWidget)
        main.addWidget(rightWidget)
        self.setLayout(main)
    
    def backend():
        upcoming = 1

if __name__ == "__main__":
    app = QApplication([])
    window = polarUI()
    window.show()
    app.exec()
