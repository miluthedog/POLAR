import cv2 as cv
import svgwrite
import xml.etree.ElementTree as ET

class Converter():
    def __init__(self):
        pass

    def img2croprgba(self, filePath):
        inImage = cv.imread(filePath, cv.IMREAD_GRAYSCALE)
        _,white = cv.threshold(inImage, 240, 255, cv.THRESH_BINARY)
        black = cv.bitwise_not(white)
        coords = cv.findNonZero(black)
        x, y, w, h = cv.boundingRect(coords)
        cropped_image = inImage[y:y+h, x:x+w]
        cropped_black = black[y:y+h, x:x+w]
        outImage = cv.cvtColor(cropped_image, cv.COLOR_GRAY2BGRA)
        outImage[:, :, 3] = cropped_black
        return outImage
    
    def croprgba2lines(self, inImage, scale, spacing): 
        height, width = inImage.shape
        resizedHeight, resizedWidth = int(height * scale), int(width * scale)
        resizedImage = cv.resize(inImage, (resizedWidth, resizedHeight))

        outImage = svgwrite.Drawing("temp.svg", size=(resizedWidth, resizedHeight))
        for y in range(0, resizedHeight, spacing):
            for x in range(resizedWidth - 1):
                brightness = resizedImage[y, x] / 255.0
                stroke_opacity = (1 - brightness)
                
                if stroke_opacity > 0:
                    outImage.add(outImage.line((x, y), (x + 1, y), stroke="black", stroke_width=1, stroke_opacity=stroke_opacity))
        return outImage

    def lines2gcode(self, inImage, feedrate, offsetX, offsetY):
        maxLaser = 255
        curX, curY, curLaser = offsetX, offsetY, 0
        '''Gcode config:
            G0 X0 Y0: move fast to 0, 0 
            G1 X0 Y0 F1000: move to 0, 0 with feed_rate 1000 mm/min
            M3 S255: turn laser on at max power
            M5: turn laser off

            G21: metric (mm unit)
            G90: absolute position mode'''
        root = ET.fromstring(inImage)
        gcode = ["G21", "G90", f"F{feedrate}"]

        for line in root.findall(".//{http://www.w3.org/2000/svg}line"):
            x1 = float(line.attrib['x1']) + offsetX
            y1 = float(line.attrib['y1']) + offsetY
            x2 = float(line.attrib['x2']) + offsetX
            opacity = float(line.attrib.get('stroke-opacity', "1.0"))
            laserPower = int(opacity * maxLaser)

            if (curX, curY) != (x1, y1):
                if curX != x1:
                    gcode.append(f"G0 X{x1} Y{y1}")
                curX, curY = x1, y1
            if curLaser != laserPower:
                gcode.append(f"M3 S{laserPower}")
                curLaser = laserPower
            gcode.append(f"G1 X{x2}")
            curX = x2

        gcode.append("M5")
        gcode.append(f"G0 X{offsetX} Y{offsetY}")
        return "\n".join(gcode)