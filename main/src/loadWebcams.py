import os
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtMultimedia import QCamera, QCameraInfo
from PyQt5.QtCore import Qt

form_assemblypage_ui = uic.loadUiType("assemblyWindow.ui")[0]

class MainWindow(QMainWindow, form_assemblypage_ui):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 사용 가능한 웹캠 목록 가져오기
        camera_infos = QCameraInfo.availableCameras()

        # 첫 번째 웹캠 초기화
        self.camera1_info = camera_infos[1] 
        self.camera1 = QCamera(self.camera1_info)
        self.viewfinder1 = QCameraViewfinder()
        self.camera1.setViewfinder(self.viewfinder1)
        self.camera1.start()

        # 두 번째 웹캠 초기화
        self.camera2_info = camera_infos[2] 
        self.camera2 = QCamera(self.camera2_info)
        self.viewfinder2 = QCameraViewfinder()
        self.camera2.setViewfinder(self.viewfinder2)
        self.camera2.start()

        # 웹캠1 프레임을 workNowLabel에 표시 - 크기조정은 학원가서 
        self.workNowLabel.setLayout(QHBoxLayout())
        self.workNowLabel.layout().addWidget(self.viewfinder1)
        # 웹캠2 프레임을 materialLabel에 표시
        self.materialLabel.setLayout(QHBoxLayout())
        self.materialLabel.layout().addWidget(self.viewfinder2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

