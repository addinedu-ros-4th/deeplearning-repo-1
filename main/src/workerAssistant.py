import os
import sys
import time 
import cv2
import torch
import numpy as np 
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from read_xml import Cxml_reader
from connect_database import Cdatabase_connect
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from ultralytics import YOLO

form_loginpage_ui = uic.loadUiType("/home/addinedu/deeplearning-repo-1/main/src/loginWindow.ui")[0]
form_selectpage_ui = uic.loadUiType("/home/addinedu/deeplearning-repo-1/main/src/selectWindow.ui")[0]
form_assemblypage_ui = uic.loadUiType("/home/addinedu/deeplearning-repo-1/main/src/assemblyWindow.ui")[0]
form_errorwindowpage_ui = uic.loadUiType("/home/addinedu/deeplearning-repo-1/main/src/errorWindow.ui")[0]
form_statisticpage_ui = uic.loadUiType("/home/addinedu/deeplearning-repo-1/main/src/statisticWindow.ui")[0]
form_servicenotready_ui = uic.loadUiType("/home/addinedu/deeplearning-repo-1/main/src/serviceNotReady.ui")[0]

inputID=''; name='' ; #사용자 정보 

# 웹캠 속성 설정
cap1 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(2)        

if cap1.isOpened():
    cap1.set(cv2.CAP_PROP_FPS, 30)
else:
    pass

if cap2.isOpened():
    cap2.set(cv2.CAP_PROP_FPS, 30)
else:
    pass
        
class MainWindow(QMainWindow, form_loginpage_ui):
    def __init__(self):
        super().__init__()
        self.setupUi(self) 
        self.loginButton.clicked.connect(self.get_login)
        self.login.hide()
        self.IDinput.textChanged.connect(self.check_text)
        
        #현재 operator id 받아오기 
        self.currentOperator = 0
        self.operatorList = self.get_operatorList()

    def showEvent(self,event):
        super().showEvent(event)
        if self.currentOperator == 0:
            self.IDinput.setText("")
            self.login.hide()

    def get_operatorList(self):
        db = Cdatabase_connect()
        result = db.get_operator()
        db.dbclose()
        return result
    
    def check_text(self):
        global inputID, name 
        id_input = self.IDinput.text()
        for val in self.operatorList:
            if id_input == str(val[0]):
                self.login.show()
                inputID=val[0]
                name = val[1]                
                self.login.setText("ID : %s 작업자 %s님 작업장으로 로그인 합니다"%(inputID,name)) 

            elif id_input == "":
                self.login.hide()

    def get_currentoperator(self,id):
        self.currentOperator = id

    def get_login(self): ## 로그인 버튼 클릭 - 로그인 정보 저장 & 선택 화면으로 넘어가기 
        id_input = self.IDinput.text()
        self.currentOperator = int(id_input)
         #선택화면으로 이동 
        self.hide() #현재 화면 숨겨주고
        selectPage = selectWindow(self) #페이지 2로 불러오고
        selectPage.get_currentoperator(self.currentOperator)
        selectPage.show()        
        

class selectWindow(QMainWindow,form_selectpage_ui):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.camera_threads = [] 
        
        self.selectDogButton.clicked.connect(self.go_assembly)
        self.selectdeskButton.clicked.connect(self.go_servicenotready)
        self.selectToyButton.clicked.connect(self.go_servicenotready)
        self.selectTableButton.clicked.connect(self.go_servicenotready)
        self.selectChairButton.clicked.connect(self.go_servicenotready)
        self.selectEtcButton.clicked.connect(self.go_servicenotready)
        
        self.checkStatisticButton.clicked.connect(self.go_statistic)
    
    def get_currentoperator(self,id):
        self.currentOperator = id

    def go_assembly(self): #작업창 이동 
        self.hide() #현재 화면 숨겨주고
        assemblyPage = assemblyWindow(self) #페이지 3 불러오고
        assemblyPage.get_currentoperator(self.currentOperator)
        assemblyPage.show() 

    def go_servicenotready(self): #작업창 이동 
        self.hide() #현재 화면 숨겨주고
        servicenotreadyPage = servicenotreadyWindow(self) 
        servicenotreadyPage.show()    
        
    def go_statistic(self): #통계페이지로 이동 
        self.hide() #현재 화면 숨겨주고
        statisticPage = statisticWindow(self) #페이지 4 불러오고
        statisticPage.get_currentoperator(self.currentOperator)
        statisticPage.show()  
        

class assemblyWindow(QMainWindow,form_assemblypage_ui):
    
    def __init__(self, parent):
        
        
        global inputID, name 
        super().__init__(parent)
        self.setupUi(self) 

        # YOLO 모델 초기화
        self.yolo_model = YOLO('/home/addinedu/deeplearning-repo-1/yolo_model/best.pt', task="detect")
        # names = self.yolo_model.names  # 클래스 이름 가져오기
    
        self.progresslist = [self.progress1, self.progress2, self.progress3, self.progress4, self.progress5,
                             self.progress6, self.progress7, self.progress8, self.progress9, self.progress10,
                             self.progress11, self.progress12, self.progress13, self.progress14, self.progress15,
                             self.progress16, self.progress17, self.progress18, self.progress19, self.progress20,
                             self.progress21, self.progress22, self.progress23, self.progress24, self.progress25,
                             self.progress26, self.progress27, self.progress28, self.progress29, self.progress30,
                             self.progress31, self.progress32, self.progress33, self.progress34, self.progress35,
                             self.progress36, self.progress37, self.progress38, self.progress39, self.progress40, 
                             self.progress41, self.progress42                             
                             ]
        self.checklist = [self.check_1,self.check_2,self.check_3,self.check_4,self.check_5,
                          self.check_6,self.check_7,self.check_8,self.check_9,self.check_10,
                          self.check_11,self.check_12,self.check_13,self.check_14,self.check_15,
                          self.check_16,self.check_17,self.check_18,self.check_19,self.check_20,
                          self.check_21,self.check_22,self.check_23,self.check_24,self.check_25,
                          self.check_26,self.check_27,self.check_28,self.check_29,self.check_30,
                          self.check_31,self.check_32,self.check_33,self.check_34,self.check_35, 
                          self.check_36,self.check_37,self.check_38,self.check_39,self.check_40,                       
                          self.check_41,self.check_42
                          ]
        
        image_path = "/home/addinedu/yolov7/mydata/images/frame_0.jpg" #올릴이미지경로설정
        pixmap = QPixmap(image_path)
        self.workNowLabel.setPixmap(pixmap)
   
        cxml = Cxml_reader("/home/addinedu/deeplearning-repo-1/main/src/workingorder.xml", "dog_light")  #xml_reader 클래스를 생성한다. 생성시 불러올 xml 주소를 인자로 넘겨준다
        self.xml_count = cxml.get_order_count() #xml안에 들어 있는 작업 순서 갯수 출력 
        self.workorderlist = cxml.get_order_list() #xml안에 들어 있는 작업순서(string)가 리스트 형태로 출력된다

        self.logoutButton.clicked.connect(self.go_main)
        self.backButton.clicked.connect(self.go_back)
        self.errorButton.clicked.connect(self.go_error)
        self.operatorList = self.get_operatorList()
        self.idLabel.setText(str(inputID))
        self.nameLabel.setText(name)

        self.workNowLabel.setAlignment(Qt.AlignCenter)
        self.materialLabel.setAlignment(Qt.AlignCenter)
        
        # 웹캠 영상을 표시하기 위해 QTimer 사용
        timer1 = QTimer(self)
        timer1.timeout.connect(self.update_frame1)
        timer1.start(1)  # 100ms마다 업데이트
        timer2 = QTimer(self)
        timer2.timeout.connect(self.update_frame2)
        timer2.start(1) 

## workGuideLabel에 가이드 이미지/영상 띄우기 --
# - 폴더내에 있는 이미지/영상 순차적으로 띄움 
# - 일단 이미지는 5초 디스플레이하고 넘어가게/ 영상은 2회 반복재생되면 넘어가게함 
        # Load the YOLOv8 model and initialize
        self.model = YOLO('/home/addinedu/deeplearning-repo-1/yolo_model/best.pt', task="detect")
        names = self.model.names
        
        # 객체 인식 메서드 호출
        self.detect_objects(image_path)
        self.media_folder = '/home/addinedu/deeplearning-repo-1/main/data/workorder/' #가이드이미지, 영상 저장된 폴더 루트 
        self.media_files = self.load_media_files()
        self.current_index = 0
        self.playback_count = 0  # 재생 횟수를 저ㅛ장하는 변수 추가

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.display_media)
        self.timer.start(1)  # 1초마다 체크
        font = QFont()
        font.setPointSize(13)
        font.setBold(True) 
        self.progressBar.setValue(0)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(42)
  
        # 객체 인식 함수 호출
        self.detect_objects(image_path)

    def detect_objects(self, image_path):
        # 이미지를 OpenCV 형식으로 로드
        image = cv2.imread(image_path)
        
        # YOLO 객체 감지
        box_results = self.model.predict(image, conf=0.5, verbose=False, show=False)
        
        for r in box_results:
            for box in r.boxes.xyxy.cpu():
                # 박스 좌표와 신뢰도 추출
                if len(box) >= 4:
                    x1, y1, x2, y2 = box[:4]  # bounding box 좌표
                    confidence = box[4] if len(box) > 4 else None  # 신뢰도
                    # 실제 길이와 픽셀 길이의 비율 계산
                    pixel_length = abs(x2 - x1)  # 정사각형의 픽셀 길이
                    real_length = 2  # 실제 길이 (여기서는 2cm)
                    pixel_to_cm_ratio = real_length / pixel_length

                    # 객체의 픽셀 좌표를 실제 길이로 변환
                    real_x1 = x1 * pixel_to_cm_ratio
                    real_x2 = x2 * pixel_to_cm_ratio
                    real_y1 = y1 * pixel_to_cm_ratio
                    real_y2 = y2 * pixel_to_cm_ratio

                    # 객체의 크기 계산
                    real_width = abs(real_x2 - real_x1)
                    real_height = abs(real_y2 - real_y1)
                    
                    # 각 객체의 박스를 OpenCV 이미지에 그립니다.
                    cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
                    
                        # 객체의 너비와 높이를 문자열로 변환
                    size_text = "Width: {:.2f} cm, Height: {:.2f} cm".format(real_width, real_height)

                    # 객체의 크기를 이미지에 표시
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.5
                    font_thickness = 1
                    font_color = (255, 255, 255)  # 흰색
                    text_size, _ = cv2.getTextSize(size_text, font, font_scale, font_thickness)
                    text_x = int((x1 + x2) / 2 - text_size[0] / 2)
                    text_y = int(y2 + text_size[1] + 5)  # 객체 아래에 위치
                    cv2.putText(image, size_text, (text_x, text_y), font, font_scale, font_color, font_thickness)

                else:
                    continue  # 값이 충분하지 않으면 다음 박스로 넘어감
                
                # 각 객체의 박스를 OpenCV 이미지에 그립니다.
                cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)

        # OpenCV 이미지를 Qt 이미지로 변환하여 표시
        q_image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_image)
        self.workNowLabel.setPixmap(pixmap)



    # def predict_byYOLO(self, img):
    #     # YOLO 객체 감지
    #     box_results = self.model.predict(img, conf = 0.5, verbose=False, show = False)
    #     boxes = box_results[0].boxes.xyxy.cpu()
    #     box_class = box_results[0].boxes.cls.cpu().tolist()

    #     names = self.model.names

    #     for r in box_results:
    #         for idx,c in enumerate(r.boxes.cls):
    #             # print("idx : {}".format(idx))
    #             # print(names[int(c.item())])
    #             pass


    def load_media_files(self): # 폴더내 모든 파일 불러와서 숫자 순서 순으로 정렬 
        media_files = []
        for file_name in os.listdir(self.media_folder):
            file_path = os.path.join(self.media_folder, file_name)
            if file_name.endswith('.jpg') or file_name.endswith('.png') or file_name.endswith('.avi'):
                media_files.append(file_path)
        media_files.sort(key=lambda x: int(os.path.basename(x).split('_')[0]))    
        return media_files

    def display_media(self): # 가이드 띄우기- 이미지/영상 
        if self.current_index < len(self.media_files):
            media_file = self.media_files[self.current_index]
            if media_file.endswith('.jpg') or media_file.endswith('.png'):
                self.display_image(media_file)
                self.current_index += 1
                self.timer.start(3000)
                #self.timer.start(5000)  # 이미지를 3초 동안 표시
            elif media_file.endswith('.avi'):
                self.display_video(media_file)
        else:
            self.timer.stop()

    def display_image(self, image_file): #이미지 띄우기 
        pixmap = QPixmap(image_file)
        fontOld = QFont() ;  fontOld.setPointSize(12); fontOld.setBold(False)
        fontNow = QFont() ;fontNow.setPointSize(12) ; fontNow.setBold(True)
        self.progresslist[self.current_index].setFont(fontNow)
        ordernow=self.progresslist[self.current_index].text()
        self.workorderLabel.setText(ordernow)
        self.checklist[self.current_index-1].setText('✔️')
        self.progresslist[self.current_index-1].setFont(fontOld)
        self.progressBar.setValue(self.current_index)
        self.workGuideLabel.setPixmap(pixmap.scaled(self.workGuideLabel.size()))

    def display_video(self, video_file): # 영상 띄우기 
        fontOld = QFont() ;  fontOld.setPointSize(12); fontOld.setBold(False)
        fontNow = QFont() ;fontNow.setPointSize(12) ; fontNow.setBold(True)
        ordernow=self.progresslist[self.current_index].text()
        self.workorderLabel.setText(ordernow)
        self.progresslist[self.current_index].setFont(fontNow)
        self.checklist[self.current_index-1].setText('✔️')
        self.progresslist[self.current_index-1].setFont(fontOld)
        self.progressBar.setValue(self.current_index)
        
        cap = cv2.VideoCapture(video_file)
        fps = cap.get(cv2.CAP_PROP_FPS)  # 영상의 프레임 속도 가져오기
        
        while True:
            ret, frame = cap.read()
            if not ret:
                self.playback_count += 1
                if self.playback_count < 2:  # 2번 반복 재생
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 영상을 처음으로 되감음
                else:
                    break
            else:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w
                q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_img)
                self.workGuideLabel.setPixmap(pixmap.scaled(self.workGuideLabel.size()))
                QApplication.processEvents()  # 이벤트 처리를 위해 프로세스 이벤트를 실행
                time.sleep(1 / fps)  # 프레임을 표시하는 간격만큼 대기      
        cap.release()
        
        self.current_index += 1  # 다음 미디어 파일로 이동
        self.playback_count = 0  # 재생 횟수 초기화
        self.timer.start(1000)  # 1초 후에 다음 미디어 파일을 표시       
# --- workGuideLabel 띄우기 끝 
                
    def update_frame1(self):
        ret, frame = cap1.read()  # 웹캠 1번
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.workNowLabel.setPixmap(pixmap)

            self.predict_byYOLO(frame)


    def update_frame2(self):
        ret, frame = cap2.read()  # 웹캠 2번
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.materialLabel.setPixmap(pixmap)
                
    ## ------캠 송출 코드     
    
    def get_currentoperator(self,id):
        self.currentOperator = id
        

    def get_operatorList(self):
        db = Cdatabase_connect()
        result = db.get_operator()
        db.dbclose()
        return result
    
    def showEvent(self,event):
        super().showEvent(event)
        self.idLabel.setText(str(self.currentOperator))

        for val in self.operatorList:
            if self.currentOperator == val[0]:
                self.nameLabel.setText(val[1])

        for idx, val in enumerate(self.workorderlist):
            tmp_txt = "{}. ".format(idx+1) +val 
            self.progresslist[idx].setText(tmp_txt)
            
                 
    def go_main(self):
        self.hide()
        self.parent().parent().get_currentoperator(0)
        self.parent().parent().show()
        
           
    def go_back(self):
        self.hide() #현재 화면 숨겨주고
        self.parent().show() #작업선택 페이지로 감 
        

    def go_error(self):
        self.hide() #현재 화면 숨겨주고
        errorPage = errorWindow(self) #에러 페이지 불러오고
        errorPage.get_currentoperator(self.currentOperator)
        errorPage.show()          
         
    
        
class errorWindow(QMainWindow,form_errorwindowpage_ui):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        global inputID, name 
        self.idLabel.setText(str(inputID))
        self.nameLabel.setText(name)  
        self.saveButton.clicked.connect(self.report_error)
        self.operatorList = self.get_operatorList()
        self.saveButton.clicked.connect(self.go_back)

    def showEvent(self,event):
        super().showEvent(event)
        self.idLabel.setText(str(self.currentOperator))

        for val in self.operatorList:
            if self.currentOperator == val[0]:
                self.nameLabel.setText(val[1])

    def get_operatorList(self):
        db = Cdatabase_connect()
        result = db.get_operator()
        db.dbclose()
        return result
    
    def go_back(self):
        self.hide() #현재 화면 숨겨주고
        self.parent().show() #작업페이지로 감 
        
    def report_error(self): #에러나면 어디로 가지? 일단 뒤로 
        self.hide() #현재 화면 숨겨주고
        self.parent().show() #작업페이지로 감 

    def get_currentoperator(self,id):
        self.currentOperator = id
       
class statisticWindow(QMainWindow,form_statisticpage_ui):
   
    def __init__(self, parent):
        super().__init__(parent)
        global inputID, name 
        self.setupUi(self)
        self.logoutButton.clicked.connect(self.go_main)
        self.backButton.clicked.connect(self.go_back)
        self.operatorList = self.get_operatorList()
      

    def showEvent(self,event):
        super().showEvent(event)
        self.idLabel.setText(str(self.currentOperator))

        self.workdataList = self.get_workdataList()

        for val in self.operatorList:
            if self.currentOperator == val[0]:
                self.nameLabel.setText(val[1])
        
        self.taskTable.clear()  

        row = self.taskTable.rowCount()

        for i in range(0,row):
            self.taskTable.removeRow(0)

        for idx, val in enumerate(self.workdataList):
            self.taskTable.insertRow(idx)
            self.taskTable.setItem(idx, 0, QTableWidgetItem(str(val[0])))
            self.taskTable.setItem(idx, 1, QTableWidgetItem(str(val[1])))
            self.taskTable.setItem(idx, 2, QTableWidgetItem(val[2]))
            self.taskTable.setItem(idx, 3, QTableWidgetItem(val[3]))


    def get_operatorList(self):
        db = Cdatabase_connect()
        result = db.get_operator()
        db.dbclose()
        return result
    
    def get_workdataList(self):
        db = Cdatabase_connect()
        result = db.get_workdata()
        db.dbclose()
        return result
    

    def get_currentoperator(self,id):
        self.currentOperator = id

    def go_main(self): #메인 이동 
        self.hide()
        self.parent().parent().get_currentoperator(0)
        self.parent().parent().show()
           
    def go_back(self):
        self.hide() #현재 화면 숨겨주고
        self.parent().show() #작업페이지로 감 

class servicenotreadyWindow(QMainWindow,form_servicenotready_ui):
   
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.backButton.clicked.connect(self.go_back)

    def go_back(self):
        self.hide() #현재 화면 숨겨주고
        self.parent().show() #작업페이지로 감 


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
