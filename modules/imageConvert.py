import cv2 as cv
import svgwrite
import io
import xml.etree.ElementTree as ET

class Converter():
    def __init__(self):
        pass

    def img2croprgba(self, filePath):
        inputImage = cv.imread(filePath, cv.IMREAD_GRAYSCALE)
        _,white = cv.threshold(inputImage, 240, 255, cv.THRESH_BINARY)
        black = cv.bitwise_not(white)
        coords = cv.findNonZero(black)
        x, y, w, h = cv.boundingRect(coords)
        croppedImage = inputImage[y:y+h, x:x+w]
        croppedBlack = black[y:y+h, x:x+w]
        outputImage = cv.cvtColor(croppedImage, cv.COLOR_GRAY2BGRA)
        outputImage[:, :, 3] = croppedBlack
        return outputImage

    def croprgba2vector(self, inputImage, scale, spacing): 
        rgbImage = inputImage[:, :, 0]
        aImage = inputImage[:, :, 3] / 255.0
        height, width = rgbImage.shape
        dwg = svgwrite.Drawing(size=(width, height))

        for y in range(0, height, spacing):
            x_start = 0
            prev_opacity = aImage[y, 0]

            for x in range(1, width):
                stroke_opacity = aImage[y, x]

                if stroke_opacity != prev_opacity:
                    dwg.add(dwg.line((x_start, y), (x - 1, y), stroke="black", stroke_width=scale, stroke_opacity=prev_opacity))
                    x_start = x
                    prev_opacity = stroke_opacity

            dwg.add(dwg.line((x_start, y), (width - 1, y), stroke="black", stroke_width=scale, stroke_opacity=prev_opacity))

        outputImage = io.StringIO()
        dwg.write(outputImage)
        return outputImage.getvalue()

    def vector2gcode(self, inputImage, feedrate, offsetX, offsetY):
        maxLaser = 255
        curX, curY, curLaser = offsetX, offsetY, 0
        '''Gcode config:
            G0 X0 Y0: move fast to 0, 0
            G1 X0 Y0 F1000: move to 0, 0 with feed_rate 1000 mm/min
            M3 S255: turn laser on at max power
            M5: turn laser off
            G21: metric (mm unit)
            G90: absolute position mode'''
        root = ET.fromstring(inputImage)
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
    
if __name__ == "__main__":
    processor = Converter()
    rgbaImage = processor.img2croprgba("test2.png")
    cv.imwrite("output.png", rgbaImage)

    svg_data = processor.croprgba2vector(rgbaImage, 1, 5)
    with open("output.svg", "w", encoding="utf-8") as f:
        f.write(svg_data)
    