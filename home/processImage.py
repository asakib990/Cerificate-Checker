import os.path
import cv2
import numpy as np
from . import utlis
from django.core.files.uploadedfile import InMemoryUploadedFile


########################################################################
# webCamFeed = True
def cropImage(image):
    img = cv2.imdecode(np.fromstring(image.read(), np.uint8), cv2.IMREAD_COLOR)
    heightImg, widthImg, c = img.shape

    imgQ = cv2.imread('home/temp/query.jpg')
    heightImg, widthImg, c = imgQ.shape
    ########################################################################

    while True:
        img = cv2.resize(img, (widthImg, heightImg))  # RESIZE IMAGE
        imgBlank = np.zeros((heightImg, widthImg, 3), np.uint8)
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # CONVERT IMAGE TO GRAY SCALE
        imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
        thres = utlis.valTrackbars()
        imgThreshold = cv2.Canny(imgBlur, thres[0], thres[1])
        kernel = np.ones((5, 5))
        imgDial = cv2.dilate(imgThreshold, kernel, iterations=2)
        imgThreshold = cv2.erode(imgDial, kernel, iterations=1)

        ## FIND ALL COUNTOURS
        imgContours = img.copy() # COPY IMAGE FOR DISPLAY PURPOSES
        imgBigContour = img.copy() # COPY IMAGE FOR DISPLAY PURPOSES
        contours, hierarchy = cv2.findContours(imgThreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # FIND ALL CONTOURS
        cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10) # DRAW ALL DETECTED CONTOURS


        # FIND THE BIGGEST COUNTOUR
        biggest, maxArea = utlis.biggestContour(contours) # FIND THE BIGGEST CONTOUR
        if biggest.size != 0:
            biggest=utlis.reorder(biggest)
            cv2.drawContours(imgBigContour, biggest, -1, (0, 255, 0), 20) # DRAW THE BIGGEST CONTOUR
            imgBigContour = utlis.drawRectangle(imgBigContour,biggest,2)
            pts1 = np.float32(biggest) # PREPARE POINTS FOR WARP
            pts2 = np.float32([[0, 0],[widthImg, 0], [0, heightImg],[widthImg, heightImg]]) # PREPARE POINTS FOR WARP
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))

            #REMOVE 20 PIXELS FORM EACH SIDE
            imgWarpColored=imgWarpColored[20:imgWarpColored.shape[0] - 20, 20:imgWarpColored.shape[1] - 20]
            imgWarpColored = cv2.resize(imgWarpColored,(widthImg,heightImg))

            # APPLY ADAPTIVE THRESHOLD
            imgWarpGray = cv2.cvtColor(imgWarpColored,cv2.COLOR_BGR2GRAY)
            imgAdaptiveThre= cv2.adaptiveThreshold(imgWarpGray, 255, 1, 1, 7, 2)
            imgAdaptiveThre = cv2.bitwise_not(imgAdaptiveThre)
            imgAdaptiveThre=cv2.medianBlur(imgAdaptiveThre,3)

            # Image Array for Display
            imageArray = ([img,imgGray,imgThreshold,imgContours],
                          [imgBigContour,imgWarpColored, imgWarpGray,imgAdaptiveThre])

        else:
            imageArray = ([img,imgGray,imgThreshold,imgContours],
                          [imgBlank, imgBlank, imgBlank, imgBlank])

        # LABELS FOR DISPLAY
        lables = [["Original","Gray","Threshold","Contours"],
                  ["Biggest Contour","Warp Prespective","Warp Gray","Adaptive Threshold"]]

        stackedImage = utlis.stackImages(imageArray,0.75,lables)

        # SAVE IMAGE WHEN 's' key is pressed

        if os.path.exists("Scanned/myImage.jpg"):
            os.remove("Scanned/myImage.jpg")
        cv2.imwrite("Scanned/myImage.jpg", imgWarpColored)
        cv2.rectangle(stackedImage, ((int(stackedImage.shape[1] / 2) - 230), int(stackedImage.shape[0] / 2) + 50), (1100, 350), (0, 255, 0), cv2.FILLED)
        cv2.putText(stackedImage, "Scan Saved", (int(stackedImage.shape[1] / 2) - 200, int(stackedImage.shape[0] / 2)), cv2.FONT_HERSHEY_DUPLEX, 3, (0, 0, 255), 5, cv2.LINE_AA)
        # cv2.waitKey(0)
        return imgWarpColored