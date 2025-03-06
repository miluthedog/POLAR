from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QPushButton, QLabel, QSizePolicy, QTextEdit, QDialog, QFileDialog, QSlider
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QIcon, QPainter, QPen, QWheelEvent, QMouseEvent, QColor, QPixmap, QImage
import os
from modules.camera import camera
from modules.connect import Arduino
from modules.firmware import GRBL
from modules.imageConvert import converter

class MainFrontEnd(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1270, 720)
        self.setWindowTitle("POLAR")
        self.setWindowIcon(QIcon("polar.ico"))

        self.backend = MainBackEnd(self)
        self.addLeftWidget()
        self.addRightWidget()

        main = QHBoxLayout()
        main.addWidget(self.leftWidget)
        main.addWidget(self.rightWidget)
        self.setLayout(main)

    def addLeftWidget(self):
        leftCombos = QHBoxLayout()
        self.comboCom, self.comboBaud = QComboBox(), QComboBox()
        self.comboCom.addItems(["COM5", "COM4", "COM3", "COM2", "COM1"])
        self.comboBaud.addItem("115200")
        for combo in (self.comboCom, self.comboBaud):
            leftCombos.addWidget(combo)


        leftButtons = QHBoxLayout()
        self.buttonFirmware, self.buttonCamera, self.buttonConnect = QPushButton("Firmware: OFF"), QPushButton("Camera: OFF"), QPushButton("OFF")
        for button in (self.buttonFirmware,self.buttonCamera):
            button.setFixedSize(90, 30)
            leftButtons.addWidget(button)
        self.buttonConnect.setFixedSize(30, 30)
        leftButtons.addWidget(self.buttonConnect)
        self.buttonFirmware.clicked.connect(self.backend.firmware)
        self.buttonCamera.clicked.connect(self.backend.camera)
        self.buttonConnect.clicked.connect(self.backend.connect)

        leftAreaLayout = QVBoxLayout()
        self.leftArea = QTextEdit()
        self.leftArea.setReadOnly(True)
        self.leftArea.setStyleSheet("background-color: #444444; color: #eeeeee; font-size: 12px; border: 1px solid #00aaaa;")
        self.leftArea.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        leftAreaLayout.addWidget(self.leftArea)

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
        for layout in (leftCombos, leftButtons, leftAreaLayout, leftMatrix):
            left.addLayout(layout)
        self.leftWidget = QWidget()
        self.leftWidget.setLayout(left)
        self.leftWidget.setFixedWidth(240)
        self.leftWidget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

    def addRightWidget(self):
        buttonPopup = QPushButton("Bottom Button")
        buttonPopup.setFixedSize(150, 40)
        buttonPopup.clicked.connect(self.backend.imageConvert)

        rightdown = QVBoxLayout()
        rightdown.addWidget(buttonPopup, alignment=Qt.AlignmentFlag.AlignCenter)
        rightdownWidget = QWidget()
        rightdownWidget.setLayout(rightdown)
        rightdownWidget.setFixedHeight(100)
        rightdownWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        righttopWidget = RightTopFullStack(self)
        righttopWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        right = QVBoxLayout()
        right.addWidget(righttopWidget)
        right.addWidget(rightdownWidget)
        self.rightWidget = QWidget()
        self.rightWidget.setLayout(right)

class MainBackEnd:
    def __init__(self, frontend):
        self.frontend = frontend
        self.connection = None
        self.responses = []
        self.popup = None

    def firmware(self):
        firmware = GRBL(self.frontend.comboCom.currentText(), self.frontend.comboBaud.currentText())
        
        if not firmware.checkFirmware():
            response = "Firmware not found. Uploading ..."
            self.responses.append(response)
            self.frontend.leftArea.setText("<br>".join(self.responses))
            uploaded, response = firmware.uploadHex()
            if not uploaded:
                self.responses.append(response)
                self.frontend.leftArea.setText("<br>".join(self.responses))
                return

        self.frontend.buttonFirmware.setText("Firmware: ON")
        response = "Firmware: ready"
        self.responses.append(response)
        self.frontend.leftArea.setText("<br>".join(self.responses))

    def camera(self):
        print("Camera functionality upcoming")

    def connect(self):
        connector = Arduino(self.frontend.comboCom.currentText(), self.frontend.comboBaud.currentText())

        if self.frontend.buttonConnect.text() == "OFF":
            self.connection, response = connector.connect(self.connection)
            if self.connection:
                self.frontend.buttonConnect.setText("ON")
        else:
            self.connection, response = connector.disconnect(self.connection)
            if not self.connection:
                self.frontend.buttonConnect.setText("OFF")

        self.responses.append(response)
        self.frontend.leftArea.setText("<br>".join(self.responses))

    def controller(self):
        print("Controller functionality upcoming")

    def imageConvert(self):
        if self.popup is None or not self.popup.isVisible():
            self.popup = PopupFrontEnd(self.frontend)
            self.popup.exec()

class RightTopFullStack(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.gridSize = 50
        self.offset = QPointF(0, 0)
        self.lastMouse = None
    
    def paintEvent(self, event):
        render = QPainter(self)
        render.setRenderHint(QPainter.RenderHint.Antialiasing)
        bigCyan, smallDcyan, bigDcyan, bigRed = QPen(Qt.GlobalColor.cyan), QPen(Qt.GlobalColor.darkCyan), QPen(Qt.GlobalColor.darkCyan), QPen(Qt.GlobalColor.red)
        for pen in (bigCyan, bigDcyan, bigRed):
            pen.setWidth(2)
        smallDcyan.setWidthF(0.5)

        render.fillRect(self.rect(), QColor(44, 44, 44))

        render.setPen(bigCyan)
        render.drawRect(self.rect().adjusted(1, 1, -1, -1))

        render.setPen(smallDcyan)
        centerX, centerY  = int(self.width() // 2 + self.offset.x()), int(self.height() // 2 + self.offset.y())
        for direction in (-1, 1):
            x, y = centerX % self.gridSize, centerY % self.gridSize
            while 0 < x < self.width():
                render.drawLine(int(x), 0, int(x), self.height())
                x += direction * self.gridSize
            while 0 < y < self.height():
                render.drawLine(0, int(y), self.width(), int(y))
                y += direction * self.gridSize

        render.setPen(bigDcyan)
        render.drawLine(0, centerY, self.width(), centerY)
        render.drawLine(centerX, 0, centerX, self.height())

        render.setPen(bigRed)
        render.drawRect(centerX, centerY, 5, 5)
    
    def wheelEvent(self, event: QWheelEvent):
        zoom = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2
        newgridSize = self.gridSize * zoom

        if 10 < newgridSize < 100:
            mousePos = event.position()
            mouseOffsetX, mouseOffsetY = mousePos.x() - self.width() / 2, mousePos.y() - self.height() / 2
            scale = newgridSize / self.gridSize
            self.offset.setX(self.offset.x() * scale + mouseOffsetX * (1 - scale))
            self.offset.setY(self.offset.y() * scale + mouseOffsetY * (1 - scale))
            self.gridSize = newgridSize
            self.update()
    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.lastMouse = event.position()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.lastMouse is not None:
            self.offset += event.position() - self.lastMouse
            self.lastMouse = event.position()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.lastMouse = None


class PopupFrontEnd(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedSize(800, 500)
        self.setWindowTitle("Image Converter")
        self.setWindowIcon(QIcon("polar.ico"))
        self.feedrateValue, self.scaleValue, self.spacingValue = 1000, 1.0, 5
        
        self.backend = PopupBackEnd(self)
        self.addLeftWidget()
        self.addRightWidget()

        popup = QHBoxLayout()
        popup.addWidget(self.leftWidget)
        popup.addWidget(self.rightWidget)
        self.setLayout(popup)

    def addLeftWidget(self):
        self.leftWidget = QLabel(self)
        self.leftWidget.setStyleSheet("border: 1px solid #00aaaa; background: #333333;")
        self.leftWidget.setScaledContents(True)
        self.leftWidget.setFixedSize(600, 450)

    def addRightWidget(self):
        buttonLayout = QHBoxLayout()
        buttonLoad, buttonDone = QPushButton("Load Image", self), QPushButton("Done", self)
        for button in (buttonLoad, buttonDone):
            button.setFixedSize(80, 30)
            buttonLayout.addWidget(button, alignment=Qt.AlignmentFlag.AlignHCenter)
        buttonLoad.clicked.connect(self.backend.loadImage)
        buttonDone.clicked.connect(self.backend.doneImage)

        sliderLayout = QHBoxLayout()
        sliderFeedrate, sliderScale, sliderSpacing = QSlider(Qt.Orientation.Vertical), QSlider(Qt.Orientation.Vertical), QSlider(Qt.Orientation.Vertical)
        for slider in (sliderFeedrate, sliderScale, sliderSpacing):
            slider.setFixedHeight(250)
            slider.setMinimum(1)
            slider.setMaximum(20)
            sliderLayout.addWidget(slider)
        sliderFeedrate.setValue(20)
        sliderScale.setValue(10)
        sliderSpacing.setValue(5)
        sliderFeedrate.valueChanged.connect(self.getFeedrate)
        sliderScale.valueChanged.connect(self.getScale)
        sliderSpacing.valueChanged.connect(self.getSpacing)

        rowLayout = QVBoxLayout()
        self.labelFeedrate = QLabel(f"Feedrate: {self.feedrateValue}", self)
        self.labelScale = QLabel(f"Size: {self.scaleValue}", self)
        self.labelSpacing = QLabel(f"Line Spacing: {self.spacingValue}", self)
        buttonFeedrate, buttonScale, buttonSpacing = QPushButton("?"), QPushButton("?"), QPushButton("?")
        rowFeedrate, rowScale, rowSpacing = QHBoxLayout(), QHBoxLayout(), QHBoxLayout()
        for label, button, row in zip([self.labelFeedrate, self.labelScale, self.labelSpacing], [buttonFeedrate, buttonScale, buttonSpacing], [rowFeedrate, rowScale, rowSpacing]):
            button.setFixedSize(20, 20)
            row.addWidget(label)
            row.addWidget(button)
            rowLayout.addLayout(row)
        buttonFeedrate.clicked.connect(self.backend.hintFeedrate)
        buttonScale.clicked.connect(self.backend.hintScale)
        buttonSpacing.clicked.connect(self.backend.hintSpacing)

        right = QVBoxLayout()
        for layout in (buttonLayout, sliderLayout, rowLayout):
            right.addLayout(layout)
        self.rightWidget = QWidget()
        self.rightWidget.setLayout(right)

    def getFeedrate(self, value):
        self.feedrateValue = value * 50
        self.labelFeedrate.setText(f"Feedrate: {self.feedrateValue}")

    def getScale(self, value):
        self.scaleValue = value / 10
        self.labelScale.setText(f"Size: {self.scaleValue:.1f}")

    def getSpacing(self, value):
        self.spacingValue = value
        self.labelSpacing.setText(f"Line Spacing: {self.spacingValue}")

class PopupBackEnd:
    def __init__(self, frontend):
        self.frontend = frontend

    def loadImage(self):
        initialDir = os.path.dirname(os.path.abspath(__file__))
        pathFilter = "Image Files (*.png *.jpg);;Vector Files (*.svg *.pdf);;All Files (*)"
        filePath, _ = QFileDialog.getOpenFileName(self.frontend, "Select Image", initialDir, pathFilter)
        image, height, width, bytesLine = converter(filePath).img2croprgba()

        qImage = QImage(image.data, width, height, bytesLine, QImage.Format.Format_RGBA8888)
        qPixmap = QPixmap.fromImage(qImage)
        self.frontend.leftWidget.setPixmap(qPixmap)
    
    def doneImage(self):
        self.frontend.accept()
    
    def hintFeedrate(self):
        pass
    
    def hintScale(self):
        pass
    
    def hintSpacing(self):
        pass

if __name__ == "__main__":
    app = QApplication([])
    window = MainFrontEnd()
    window.show()
    app.exec()
