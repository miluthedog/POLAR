from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QPushButton, QLabel, QSizePolicy, QTextEdit
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QIcon, QPainter, QPen, QWheelEvent, QMouseEvent, QColor
from modules.camera import camera
from modules.connect import Arduino
from modules.firmware import GRBL
from modules.imageConvert import png2gcode

class FrontEnd(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1270, 720)
        self.setWindowTitle("POLAR")
        self.setWindowIcon(QIcon("polar.ico"))

        self.backend = BackEnd(self)
        self.addLeftWidget()
        self.addRightWidget()

        main = QHBoxLayout()
        main.addWidget(self.leftWidget)
        main.addWidget(self.rightWidget)
        self.setLayout(main)

    def addLeftWidget(self):
        leftCombos = QHBoxLayout()
        self.combo1 = QComboBox()
        self.combo2 = QComboBox()
        self.combo1.addItems(["COM5", "COM4", "COM3", "COM2", "COM1"])
        self.combo2.addItem("115200")
        leftCombos.addWidget(self.combo1)
        leftCombos.addWidget(self.combo2)

        leftButtons = QHBoxLayout()
        self.button1 = QPushButton("Firmware: OFF")
        self.button2 = QPushButton("Camera: OFF")
        self.button3 = QPushButton("OFF")
        self.button1.setFixedSize(90, 30)
        self.button2.setFixedSize(90, 30)
        self.button3.setFixedSize(30, 30)
        self.button1.clicked.connect(self.backend.firmware)
        self.button2.clicked.connect(self.backend.camera)
        self.button3.clicked.connect(self.backend.connect)
        leftButtons.addWidget(self.button1)
        leftButtons.addWidget(self.button2)
        leftButtons.addWidget(self.button3)

        self.leftArea = QTextEdit()
        self.leftArea.setReadOnly(True)
        self.leftArea.setStyleSheet("background-color: #444444; color: #eeeeee; font-size: 12px; border: 1px solid #00aaaa;")
        self.leftArea.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        leftMatrix = QGridLayout()
        matrix = []
        matrixLabels = [["NW", "N", "NE"],
                        ["W", "🏠", "E"],
                        ["SW", "S", "SE"]]
        for row in range(3):
            for col in range(3):
                button = QPushButton(matrixLabels[row][col])
                button.setFixedSize(60, 60)
                matrix.append(button)
                leftMatrix.addWidget(button, row, col)
        for button in matrix:
            button.clicked.connect(self.backend.controller)

        left = QVBoxLayout()
        left.addLayout(leftCombos)
        left.addLayout(leftButtons)
        left.addWidget(self.leftArea)
        left.addLayout(leftMatrix)
        self.leftWidget = QWidget()
        self.leftWidget.setLayout(left)
        self.leftWidget.setFixedWidth(240)
        self.leftWidget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

    def addRightWidget(self):
        buttonBig = QPushButton("Bottom Button")
        buttonBig.setFixedSize(150, 40)
        buttonBig.clicked.connect(self.backend.imageConvert)

        rightdown = QVBoxLayout()
        rightdown.addWidget(buttonBig, alignment=Qt.AlignmentFlag.AlignCenter)
        rightdownWidget = QWidget()
        rightdownWidget.setLayout(rightdown)
        rightdownWidget.setFixedHeight(100)
        rightdownWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        righttopWidget = RightTopBackEnd(self)
        righttopWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        right = QVBoxLayout()
        right.addWidget(righttopWidget)
        right.addWidget(rightdownWidget)
        self.rightWidget = QWidget()
        self.rightWidget.setLayout(right)

class BackEnd:
    def __init__(self, frontend):
        self.frontend = frontend
        self.connection = None
        self.responses = []

    def firmware(self):
        firmware = GRBL(self.frontend.combo1.currentText(), self.frontend.combo2.currentText())
        alreadyGrbl = firmware.checkFirmware()
        if not alreadyGrbl:
            response = "Uploading firmware..."
            firmware.uploadHex()
            self.responses.append(response)
        self.frontend.button1.setText("Firmware: ON")
        response = "Firmware: ready"
        self.responses.append(response)
        self.frontend.leftArea.setText("<br>".join(self.responses))

    def camera(self):
        print("Camera functionality upcoming")

    def connect(self):
        connector = Arduino(self.frontend.combo1.currentText(), self.frontend.combo2.currentText())
        if self.frontend.button3.text() == "OFF":
            self.connection, response = connector.connect(self.connection)
            if self.connection:
                self.frontend.button3.setText("ON")
        else:
            self.connection, response = connector.disconnect(self.connection)
            if not self.connection:
                self.frontend.button3.setText("OFF")

        self.responses.append(response)
        self.frontend.leftArea.setText("<br>".join(self.responses))

    def controller(self):
        print("Controller functionality upcoming")

    def imageConvert(self):
        print("Image conversion functionality upcoming")

class RightTopBackEnd(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gridSize = 50
        self.offset = QPointF(0, 0)
        self.lastMouse = None
    
    def paintEvent(self, event):
        render = QPainter(self)
        render.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        render.fillRect(self.rect(), QColor(44, 44, 44))
        
        borderPen = QPen(Qt.GlobalColor.cyan)
        borderPen.setWidth(2)
        render.setPen(borderPen)
        render.drawRect(self.rect().adjusted(1, 1, -1, -1))
        
        grid = QPen(Qt.GlobalColor.darkCyan)
        grid.setWidthF(0.5)
        render.setPen(grid)
        centerX = int(self.width() // 2 + self.offset.x())
        centerY = int(self.height() // 2 + self.offset.y())
        for direction in (-1, 1):
            x = centerX % self.gridSize
            y = centerY % self.gridSize
            while 0 < x < self.width():
                render.drawLine(int(x), 0, int(x), self.height())
                x += direction * self.gridSize
            while 0 < y < self.height():
                render.drawLine(0, int(y), self.width(), int(y))
                y += direction * self.gridSize

        coord = QPen(Qt.GlobalColor.darkCyan)
        coord.setWidth(2)
        render.setPen(coord)
        render.drawLine(0, centerY, self.width(), centerY)
        render.drawLine(centerX, 0, centerX, self.height())

        origin = QPen(Qt.GlobalColor.red)
        render.setPen(origin)
        render.drawRect(centerX, centerY, 5, 5)
    
    def wheelEvent(self, event: QWheelEvent):
        zoom = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2
        newgridSize = self.gridSize * zoom
        if 10 < newgridSize < 100:
            mousePos = event.position()
            mouseOffsetX = mousePos.x() - self.width() / 2
            mouseOffsetY = mousePos.y() - self.height() / 2
            scale = newgridSize / self.gridSize
            self.offset.setX(self.offset.x() * scale + mouseOffsetX * (1 - scale))
            self.offset.setY(self.offset.y() * scale + mouseOffsetY * (1 - scale))
            
            self.gridSize = newgridSize
            self.update()
    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.lastMouse = event.position()

    def mouseMoveEvent(self, ev: QMouseEvent):
        if self.lastMouse is not None:
            delta = ev.position() - self.lastMouse
            self.offset += delta
            self.lastMouse = ev.position()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.lastMouse = None

if __name__ == "__main__":
    app = QApplication([])
    window = FrontEnd()
    window.show()
    app.exec()
