import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
import cv2
import time
from PyQt5.QtCore import QThread
from PyQt5 import QtCore
import datetime

class Camera(QThread):
    update = QtCore.pyqtSignal()

    def __init__(self, sec =0, parent = None):
        super().__init__()
        self.main = parent
        self.running = True

    def run(self):
        count =0
        while self.running == True:
            self.update.emit()
            time.sleep(0.1)

    def stop(self):
        self.running = False


from_class = uic.loadUiType("opencv.ui")[0]

class WindowClass(QMainWindow, from_class) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.camera = Camera(self)
        self.camera.daemon = True

        self.record = Camera(self)
        self.record.daemon = True

        self.playvideo = Camera(self)
        self.playvideo.daemon = True

        self.image = None
        self.count = 0
        self.frameCount =0

        self.isCameraOn = False
        self.isRecStart = False
        self.btnRecord.hide()
        self.btnCapture.hide()

        self.pixmap = QPixmap()
        self.btnOpen.clicked.connect(self.openFile)
        self.btnCamera.clicked.connect(self.clickCamera)
        self.camera.update.connect(self.updateCamera)
        self.btnRecord.clicked.connect(self.clickRecord)
        self.record.update.connect(self.updateRecording)
        self.btnCapture.clicked.connect(self.capture)
        self.playvideo.update.connect(self.updateVideoPlayer)

    def capture(self):
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.now + ".png"

        cv2.imwrite(filename, self.image)

    def updateRecording(self):
        self.writer.write(self.image)
        # self.label2.setText(str(self.count))
        # self.count +=1

    def clickRecord(self):
        if self.isRecStart == False:
            self.btnRecord.setText("Rec Stop")
            self.isRecStart = True
            self.recordingStart()

        else:
            self.btnRecord.setText("Rec Start")
            self.isRecStart = False
            self.recordingStop()

    def recordingStart(self):
        self.record.running = True
        self.record.start()

        self.now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.now + ".avi"
        self.fourcc = cv2.VideoWriter_fourcc(*"XVID")
        
        w = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        self.writer = cv2.VideoWriter(filename, self.fourcc, 20.0, (w,h))

    def recordingStop(self):
        self.record.running = False

        if self.isRecStart == True:
            self.writer.release()


    def updateCamera(self):
        retval, image = self.video.read()
        if retval:
            self.image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            h,w,c = self.image.shape
            qimage = QImage(self.image.data, w, h, w*c, QImage.Format_RGB888)

            self.pixmap = self.pixmap.fromImage(qimage)
            self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())

            self.label.setPixmap(self.pixmap)
        # self.label.setText("Camera Running : " + str(self.count))
        self.count += 1

    def clickCamera(self):
        if self.isCameraOn == False:
            self.btnCamera.setText("Camera Off")
            self.isCameraOn = True
            self.btnRecord.show()
            self.btnCapture.show()

            self.cameraStart()
        else:
            self.btnCamera.setText("Camera On")
            self.isCameraOn = False
            self.btnRecord.hide()
            self.btnCapture.hide()
            self.cameraStop()
            self.recordingStop()

    def cameraStart(self):
        self.camera.running = True
        self.camera.start()
        self.video = cv2.VideoCapture(2)

    def cameraStop(self):
        self.camera.running = False
        self.count =0
        self.video.release

    def openFile(self):
        file = QFileDialog.getOpenFileName(filter="Image (*.jpg *.avi);;")

        if ".jpg" in file[0]:
            image = cv2.imread(file[0])
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            h,w,c = image.shape
            qimage = QImage(image.data, w,h, w*c, QImage.Format_RGB888)

            self.pixmap = self.pixmap.fromImage(qimage)
            self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())

            self.label.setPixmap(self.pixmap)
        else:
            self.videoplayStart(file[0])


    def videoplayStart(self,filename):
        self.playvideo.running = True
        self.playvideo.start()
        self.videoplayer = cv2.VideoCapture("protocol://host:port/script_name?script_params|auth")

    def videoplayStop(self):
        self.playvideo.running = False
        self.videoplayer.release()

    def updateVideoPlayer(self):
        retval, image = self.videoplayer.read()
        if self.videoplayer.get(cv2.CAP_PROP_POS_FRAMES) == self.videoplayer.get(cv2.CAP_PROP_FRAME_COUNT):
                    self.videoplayer.set(cv2.CAP_PROP_POS_FRAMES,0)
                    self.videoplayStop()
        if retval:
            self.tmpvideoframe = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h,w,c = self.tmpvideoframe.shape    
            qimage = QImage(self.tmpvideoframe.data, w, h, w*c, QImage.Format_RGB888)
            self.tmpvideoframe = cv2.cvtColor(self.tmpvideoframe, cv2.COLOR_BGR2RGB)
            self.pixmap = self.pixmap.fromImage(qimage)
            self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())
            self.label.setPixmap(self.pixmap)



            
            # print(file[0])
            # for i in range(0,100):
            #     retval, image = self.playvideo.read()
            #     self.frameCount +=1
            #     print(retval)
            #     print(image)
            #     print(self.frameCount)

            #     if retval:
            #         self.playvideo = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            #         h,w,c = self.playvideo.shape
            #         self.playvideo = cv2.cvtColor(self.playvideo, cv2.COLOR_BGR2RGB)

            #         qimage = QImage(self.playvideo.data, w, h, w*c, QImage.Format_RGB888)


            #         self.pixmap = self.pixmap.fromImage(qimage)
            #         self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())

            #         self.label.setPixmap(self.pixmap)



            

                






if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()

    sys.exit(app.exec_())