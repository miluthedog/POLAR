from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDialog, QFileDialog, QSlider
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QImage
import os
from modules.imageConvert import converter

class PopupFrontEnd(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedSize(800, 500)
        self.setWindowTitle("Image Converter")
        self.setWindowIcon(QIcon("Assests/polar.ico"))
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
        if filePath:
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