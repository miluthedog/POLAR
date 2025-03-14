from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDialog, QFileDialog, QSlider, QApplication
from PyQt6.QtCore import Qt, QEvent, QPoint, QByteArray, QSize
from PyQt6.QtGui import QIcon, QPixmap, QImage, QPainter
from PyQt6.QtSvg import QSvgRenderer
import os
from modules.imageConvert import Converter


class PopupFrontEnd(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(800, 500)
        self.setWindowTitle("Image Converter")
        self.setWindowIcon(QIcon("Assets/polar.ico"))
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
        buttonFeedrate = HintButton("?", "Laser movement speed, based on materials:\n- Wood: 1000\n- Cardboard: 800", self)
        buttonScale = HintButton("?", "Rescales the image", self)
        buttonSpacing = HintButton("?", "Spacing between lines", self)
        rowFeedrate, rowScale, rowSpacing = QHBoxLayout(), QHBoxLayout(), QHBoxLayout()
        for label, button, row in zip([self.labelFeedrate, self.labelScale, self.labelSpacing], [buttonFeedrate, buttonScale, buttonSpacing], [rowFeedrate, rowScale, rowSpacing]):
            button.setFixedSize(20, 20)
            row.addWidget(label)
            row.addWidget(button)
            rowLayout.addLayout(row)

        right = QVBoxLayout()
        for layout in (buttonLayout, sliderLayout, rowLayout):
            right.addLayout(layout)
        self.rightWidget = QWidget()
        self.rightWidget.setLayout(right)

    def getFeedrate(self, value):
        self.feedrateValue = value * 50
        self.labelFeedrate.setText(f"Feedrate: {self.feedrateValue}")
        self.backend.updateImage()

    def getScale(self, value):
        self.scaleValue = value / 10
        self.labelScale.setText(f"Size: {self.scaleValue:.1f}")
        self.backend.updateImage()

    def getSpacing(self, value):
        self.spacingValue = value
        self.labelSpacing.setText(f"Line Spacing: {self.spacingValue}")
        self.backend.updateImage()


class PopupBackEnd:
    def __init__(self, frontend):
        self.frontend = frontend
        self.offsetX, self.offsetY = 0, 0
        self.filePath = None
        self.croprgba = None
        self.gcode = None

    def loadImage(self):
        initialDir = os.path.dirname(os.path.abspath(__file__))
        pathFilter = "Image Files (*.png *.jpg);;Vector Files (*.svg *.pdf);;All Files (*)"
        self.filePath, _ = QFileDialog.getOpenFileName(self.frontend, "Select Image", initialDir, pathFilter)
        if self.filePath:
            self.croprgba = Converter().img2croprgba(self.filePath)

    def updateImage(self):
        if self.filePath:
            self.svgString, width, height = Converter().croprgba2vector(self.croprgba, self.frontend.scaleValue, self.frontend.spacingValue)
            svgBytes = QByteArray(self.svgString.encode('utf-8'))                   # decode svg string
            renderer = QSvgRenderer(svgBytes)                                       # set up svg "renderer"
            svgQimage = QImage(QSize(width, height), QImage.Format.Format_ARGB32)   # set up qImage
            svgQimage.fill(0)
            painter = QPainter(svgQimage)                                           # set up qPainter
            renderer.render(painter)                                                
            painter.end()            

            qPixmap = QPixmap.fromImage(svgQimage)                                  # convert to qPixmap (require 3 set up)
            self.frontend.leftWidget.setPixmap(qPixmap)
            # alway available draging -> update offset

    def doneImage(self):
        if self.frontend.accept():
            self.gcode = Converter().lines2gcode(self.lines, self.frontend.feedrateValue, self.offsetX, self.offsetY)

    def getGcode(self):
        return self.gcode


class HintButton(QPushButton):
    def __init__(self, text, hint, parent=None):
        super().__init__(text, parent)
        self.hint = hint

        self.tooltip = QLabel(self.hint, parent)
        self.tooltip.setStyleSheet("background: gray; border: 1px solid #00aaaa; padding: 5px;")
        self.tooltip.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.tooltip.hide()

        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == QEvent.Type.Enter:
                self.showTooltip()
            elif event.type() == QEvent.Type.Leave:
                self.tooltip.hide()
        return super().eventFilter(obj, event)

    def showTooltip(self):
        pos = self.mapToGlobal(QPoint(self.width() + 5, 0))
        self.tooltip.move(pos)
        self.tooltip.show()


if __name__ == "__main__":
    app = QApplication([])
    window = PopupFrontEnd()
    window.show()
    app.exec()