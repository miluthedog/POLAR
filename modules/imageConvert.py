import cv2 as cv


class converter():
    def __init__(self, filePath):
        self.filePath = filePath

    def img2croprgba(self):
        inImage = cv.imread(self.filePath, cv.IMREAD_GRAYSCALE)
        _,white = cv.threshold(inImage, 240, 255, cv.THRESH_BINARY)
        black = cv.bitwise_not(white)
        coords = cv.findNonZero(black)
        x, y, w, h = cv.boundingRect(coords)
        cropped_image = inImage[y:y+h, x:x+w]
        cropped_black = black[y:y+h, x:x+w]
        outImage = cv.cvtColor(cropped_image, cv.COLOR_GRAY2BGRA)
        outImage[:, :, 3] = cropped_black
        height, width, channel = outImage.shape
        bytesLine = channel * width
        return outImage, height, width, bytesLine