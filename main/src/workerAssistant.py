import os
import sys
import time 
import cv2
import torch
import numpy as np 
import atexit
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
import pandas as  pd 
from datetime import datetime 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import koreanize_matplotlib
import mediapipe as mp
from tensorflow.keras.models import load_model
from PyQt5.QtWidgets import QMessageBox
import resource
import time
import torchvision.transforms as transforms

TESTMODE = 0 #gui 테스트 하실때는 1

form_loginpage_ui = uic.loadUiType("loginWindow.ui")[0]
form_selectpage_ui = uic.loadUiType("selectWindow.ui")[0]
form_assemblypage_ui = uic.loadUiType("assemblyWindow.ui")[0]
form_errorwindowpage_ui = uic.loadUiType("errorWindow.ui")[0]
form_statisticpage_ui = uic.loadUiType("statisticWindow.ui")[0]
form_servicenotready_ui = uic.loadUiType("serviceNotReady.ui")[0]

inputID=''; name=''; workname=''; errorpart=''; errorReason='' #사용자 정보 
global_work_data = pd.DataFrame(columns=['작업명',' ID ', '작업자',  ' 작업 날짜 ','작업 상태'])
global_error_data = pd.DataFrame(columns=['작업명','ID', '작업자',  '작업 날짜','불량 단계', '불량 사유'])

#yolo_model_path 
yolo_path = '../../model/best.pt'
step_yolo_path = '../../model/step_model_best.pt'
mp_path = '../../model/model_cnn_mediapipe_vector2.h5'
# 웹캠 속성 설정

available_index = []
for index in range(5): 
    camera = cv2.VideoCapture(index)
    if camera.isOpened():
        available_index.append(index)
        camera.release()
if len(available_index)==2:
    cap1 = cv2.VideoCapture(available_index[0])
    cap2 = cv2.VideoCapture(available_index[1])
elif len(available_index)==1:
    cap1 = cv2.VideoCapture(available_index[0])     
    cap2 = cv2.VideoCapture('../data/work_view_rgb.avi')
else:
    cap1=cv2.VideoCapture(0); cap2 =cv2.VideoCapture(2)

if cap1.isOpened():
    cap1.set(cv2.CAP_PROP_FPS, 30)
else:
    print("camera 1 is not open")
    
    cap2 = cv2.VideoCapture('../data/material_view_rgb.avi')
    cap1 = cv2.VideoCapture('../data/work_view_rgb.avi')

if cap2.isOpened():
    cap2.set(cv2.CAP_PROP_FPS, 30)
else:
    print("camera 2 is not open")
    
#mediapipe hand 속성 설정



# def function_to_measure():
#     # 리소스를 측정할 함수
#     for _ in range(1000000):
#         _ = 1 + 1

def cleanup():
    cap1.release()
    cap2.release()
    print("release")
    
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
        self.parent = parent 
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
        global workname 
        workname='후아유 강아지 조명'
        self.hide() #현재 화면 숨겨주고
        assemblyPage = assemblyWindow(parent=self.parent) #페이지 3 불러오고
        assemblyPage.get_currentoperator(inputID)
        assemblyPage.show() 

    def go_servicenotready(self): #작업창 이동 
        self.hide() #현재 화면 숨겨주고
        servicenotreadyPage = servicenotreadyWindow(parent=self.parent) 
        servicenotreadyPage.show()    
        
    def go_statistic(self): #통계페이지로 이동 
        self.hide() #현재 화면 숨겨주고
        statisticPage = statisticWindow(parent=self.parent) #페이지 4 불러오고
        statisticPage.get_currentoperator(inputID)
        statisticPage.show()
                
class assemblyWindow(QMainWindow,form_assemblypage_ui):
    
    def __init__(self, parent):
        
        
        global inputID, name 
        super().__init__(parent)
        self.setupUi(self) 
        self.parent = parent

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
        
        cxml = Cxml_reader("workingorder.xml", "dog_light")  #xml_reader 클래스를 생성한다. 생성시 불러올 xml 주소를 인자로 넘겨준다
        self.xml_count = cxml.get_order_count() #xml안에 들어 있는 작업 순서 갯수 출력 
        self.workorderlist = cxml.get_order_list() #xml안에 들어 있는 작업순서(string)가 리스트 형태로 출력된다
        
        cxml_objectdetect = Cxml_reader("objectdetectlist_test.xml", "dog_light")
        # cxml_objectdetect = Cxml_reader("objectdetectlist.xml", "dog_light")
        self.xml_detection_modellist = cxml_objectdetect.get_model_list() #xml안에 yolo 모델 리스트 출력 
        self.xml_detection_countlist = cxml_objectdetect.get_object_count_list() #xml안에 들어 있는 yolo 모델이 해당 스텝에 인식해야 할 object 갯수 출력
        self.xml_detection_partlist = cxml_objectdetect.get_object_parts_list() #xml안에 들어 있는 yolo 모델이 해당 스텝에 인식해야 하는 파트 이름 출력
        
        self.logoutButton.clicked.connect(self.go_main)
        self.backButton.clicked.connect(self.go_back)
        self.errorButton.clicked.connect(self.go_error)
        self.operatorList = self.get_operatorList()
        self.idLabel.setText(str(inputID))
        self.nameLabel.setText(name)

        self.workNowLabel.setAlignment(Qt.AlignCenter)
        self.materialLabel.setAlignment(Qt.AlignCenter)
        self.startButton.hide()
        self.startButton.clicked.connect(self.restart_assembly)
        self.quitButton.hide()
        self.quitButton.clicked.connect(self.quitWork)
        
        # 웹캠 영상을 표시하기 위해 QTimer 사용
        timer1 = QTimer(self)
        timer1.timeout.connect(self.update_frame1)
        timer1.start(1)  # 100ms마다 업데이트
        timer2 = QTimer(self)
        timer2.timeout.connect(self.update_frame2)
        timer2.start(1) 

        # Load the YOLOv8 model
        self.model = YOLO(yolo_path)
        self.stepmodel = YOLO(step_yolo_path)
        self.yolo_detect_class = []
        self.yolo_detect_class_coordinate = []
        self.yolo_detect_class_workview = []
        self.yolo_detect_class_coordinate_workview = []
        
        #Load the Mediapipe model
        self.mp_model = load_model(mp_path)
        self.is_grabbing = False
        

        self.stepmodel_timecount = 0
        self.iscorrecttimer_on =0
        self.correcttimer = 0


    
## workGuideLabel에 가이드 이미지/영상 띄우기 --
# - 폴더내에 있는 이미지/영상 순차적으로 띄움 
# - 일단 이미지는 5초 디스플레이하고 넘어가게/ 영상은 2회 반복재생되면 넘어가게함 
        
        # 객체 인식 메서드 호출
        self.media_folder = '/home/dyjung/amr_ws/ml/project/data/workorder/' #가이드이미지, 영상 저장된 폴더 루트 
        self.media_files = self.load_media_files()
        self.current_index = 20
        self.set_yolochecklist(self.current_index)
        self.playback_count = 0  # 재생 횟수를 저장하는 변수 추가

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.display_media)
        self.timer.start(1)  # 1초마다 체크
        font = QFont()
        font.setPointSize(13)
        font.setBold(True) 
        self.progressBar.setValue(0)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(42)
        self.fontOld = QFont() ;  self.fontOld.setPointSize(12); self.fontOld.setBold(False)
        self.fontNow = QFont() ;self.fontNow.setPointSize(13) ; self.fontNow.setBold(True)
        self.fontCheck= QFont(); self.fontCheck.setPointSize(11);self.fontCheck.setBold(True)
        self.ordernow = ''
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode = True, max_num_hands = 1, min_detection_confidence = 0.3)

        if torch.cuda.is_available():
    # GPU를 사용하도록 설정
            self.device = torch.device("cuda")
            print("GPU를 사용합니다.")
        else:
        # CPU를 사용하도록 설정
            self.device = torch.device("cpu")
            print("GPU를 사용할 수 없습니다. CPU를 사용합니다.")
    

    def convert_to_torchtensor(self, num_data):
        transform = transforms.ToTensor()
        tensor_data = transform(num_data)
        return tensor_data  
    
    def move_to_device(self, data):
        # GPU로 이동
        tensor_data = data.to(self.device)
        return tensor_data

        

    def quitWork(self):
        global global_work_data, inputID,name,workname
        finishment='완료'
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        work_report=pd.DataFrame({'작업명': [workname],' ID ': [inputID], '작업자': [name], ' 작업 날짜 ':[formatted_time] ,'작업 상태': [finishment]})
        #global_work_data = pd.concat([global_work_data, work_report], ignore_index=True)
        db = Cdatabase_connect()
        db.insert_workdata(workname,inputID,name,formatted_time,finishment) 
        db.dbclose()
        self.hide()
        selectPage = selectWindow(parent=self.parent) #페이지 2로 불러오고
        selectPage.get_currentoperator(inputID)
        selectPage.show()  
        
    def restart_assembly(self):
        global global_work_data, inputID,name,workname
        finishment='완료'
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        work_report=pd.DataFrame({'작업명': [workname],' ID ': [inputID], '작업자': [name], ' 작업 날짜 ':[formatted_time] ,'작업 상태': [finishment]})
        #global_work_data = pd.concat([global_work_data, work_report], ignore_index=True)
        db = Cdatabase_connect()
        db.insert_workdata(workname,inputID,name,formatted_time,finishment)       
        db.dbclose()
        # 현재 창 닫기
        self.close()
        # 새 assemblyWindow 창 열기
        new_assembly_window = assemblyWindow(parent=self.parent)
        new_assembly_window.get_currentoperator(inputID)
        new_assembly_window.show()
    
    # 손가락의 좌표와 잡아야 하는 object check 
    # - 1)객체의 x,x1,y,y1 의 좌표에서 +a 만큼의 오차를 주어 2)손가락의 끝점 좌표로 그 영역에 들어가면 올바르게 잡았다고 확인
    # - 1) 과 2) 가 모두 True일때 다음 step으로 넘어감 (허공에서 grab을 했을 경우 제외)
        
    def object_grab_check(self, xy_list ):
        
        # grab_flag = False
        
        hand_landmark_list = [4, 8, 12, 16, 20]  # 손 끝점 
        error = 5  # 오차

        # 각 좌표 리스트에 대해 처리
        for coord in xy_list:
            # 좌표 리스트의 각 좌표에 오차를 적용하여 사각형의 좌표를 계산
            rect = [(coord[0] - error, coord[1] + error), 
                    (coord[1] + error, coord[1] + error), 
                    (coord[1] + error, coord[3] - error), 
                    (coord[0] - error, coord[3] - error)]

            # 손의 끝점이 사각형 범위 안에 있는지 확인
            if self.mp_results.multi_hand_landmarks:
                for hand_landmarks in self.mp_results.multi_hand_landmarks: 
                    for index in hand_landmark_list:
                        obj_grab_result = cv2.pointPolygonTest(rect, (hand_landmarks.landmark[index].x, hand_landmarks.landmark[index].y), False) 
                        # x, y가 사각형 범위 안에 있는지 확인 (bool)
                        # 만약 어떤 좌표에도 해당되지 않는다면 -1을 반환하므로, 해당 조건을 처리할 필요가 있습니다.
                        if obj_grab_result != -1:
                            return obj_grab_result

        return False  # 모든 좌표 리스트에 대해 손의 끝점이 범위 안에 없으면 False를 반환
                    

    def mp_update(self, frame_for_mp):
        
        self.mp_results = self.hands.process(frame_for_mp)
        
        if self.mp_results.multi_hand_landmarks:
            for hand_landmarks in self.mp_results.multi_hand_landmarks: 
                # 손가락 각 관절의 벡터 값을 추출합니다.
                finger_vectors = []
                for finger_idx in range(5):  # 각 손가락에 대해
                    for joint_idx in range(1, 5):  # 각 관절에 대해
                        # 이전 관절과 현재 관절 사이의 벡터 계산
                        vector = np.array([hand_landmarks.landmark[finger_idx * 4 + joint_idx].x - hand_landmarks.landmark[finger_idx * 4 + joint_idx - 1].x,
                                        hand_landmarks.landmark[finger_idx * 4 + joint_idx].y - hand_landmarks.landmark[finger_idx * 4 + joint_idx - 1].y,
                                        hand_landmarks.landmark[finger_idx * 4 + joint_idx].z - hand_landmarks.landmark[finger_idx * 4 + joint_idx - 1].z])
                        finger_vectors.append(vector)

                # 모델에 손가락 벡터를 입력으로 전달하여 추론합니다.
                prediction = self.mp_model.predict(np.array([finger_vectors]))
                probability = prediction[0][0]  # 확률 값
        
                # grab 상태 결정 
                self.is_grabbing = probability >= 0.5
                # self.grab_status_text = f"Grab" if is_grabbing else f"Release" # 상태는 업데이트 되므로 qimage 표시하는곳에 puttext하면됨
        else:
            self.grab_status_text = " None "
    def yolo_update(self, frame_for_yolo): #materialview
        
        self.yolo_detect_class.clear() #담기 전에 reset
        self.yolo_detect_class_coordinate.clear()
        frame_for_yolo = self.convert_to_torchtensor(frame_for_yolo)
        frame_for_yolo = self.move_to_device(frame_for_yolo)

        results = self.model.predict(frame_for_yolo, show_boxes=False)
        names = self.model.names

        for r in results:
            for idx,cls_name in enumerate(r.boxes.cls):
                tmp_name = names[int(cls_name.item())]
                if tmp_name == 'bar':
                    size = self.measure_bar_size(r.boxes.xyxy.cpu()[idx]) #bar일때만 꺼내려고 한건데 이게 맞낭..#하린님
                    if size != 0:
                        tmp_name += str(size)
                self.yolo_detect_class.append(tmp_name)
                self.yolo_detect_class_coordinate.append(r.boxes.xyxy.cpu())
                
        # print("materialview")
        # print(self.yolo_detect_class)
        # print("---")
        # print(self.yolo_detect_class_coordinate)
        
    def yolo_update_workview(self, frame_for_yolo):
        
        self.yolo_detect_class_workview.clear() #담기 전에 reset
        self.yolo_detect_class_coordinate_workview.clear()
        if self.xml_detection_modellist[self.current_index] == '0':
            results = self.model.predict(frame_for_yolo, show_boxes=False)
            names = self.model.names

            for r in results:
                for idx,cls_name in enumerate(r.boxes.cls):
                    tmp_name = names[int(cls_name.item())]
                    if tmp_name == 'bar':
                        size = self.measure_bar_size(r.boxes.xyxy.cpu()[idx]) #bar일때만 꺼내려고 한건데 이게 맞낭..#하린님
                        if size != 0:
                            tmp_name += str(size)
                    self.yolo_detect_class_workview.append(tmp_name)
                    self.yolo_detect_class_coordinate_workview.append(r.boxes.xyxy.cpu())
                
        elif self.xml_detection_modellist[self.current_index] == '1':
            results = self.stepmodel.predict(frame_for_yolo, show_boxes=False)
            stepnames = self.stepmodel.names

            for r in results:
                for cls_name in r.boxes.cls:
                    tmp_name = stepnames[int(cls_name.item())]
                    self.yolo_detect_class_workview.append(tmp_name)
                    self.yolo_detect_class_coordinate_workview.append(r.boxes.xyxy.cpu())

        # print("workview")
        # print(self.yolo_detect_class_workview)
        # print("---")
        # print(self.yolo_detect_class_coordinate)
        
    def draw_rec(self,img_form): #workview
        result = img_form.copy()

        for val in self.yolo_detect_class_coordinate_workview:
            for idx, coord in enumerate(val):
                x1 = coord[0]
                y1 = coord[1]
                x2 = coord[2]
                y2 = coord[3]
                cv2.rectangle(result, (int(x1.item()), int(y1.item())), (int(x2.item()), int(y2.item())), (255, 0, 0), 2)
                
                # print("x1 : {}, y1: {} x2: {} y2: {}".format(int(x1), int(y1)), (int(x2), int(y2)))
                # 객체의 크기를 이미지에 표시
                
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                font_thickness = 1
                font_color = (255, 255, 255)  # 흰색
                
                text_size, _ = cv2.getTextSize(self.yolo_detect_class_workview[idx], font, font_scale, font_thickness)
                text_x = int((x1 + x2) / 2 - text_size[0] / 2)
                text_y = int(y2 + text_size[1] + 5)  # 객체 아래에 위치
                cv2.putText(result, self.yolo_detect_class_workview[idx], (text_x, text_y), font, font_scale, font_color, font_thickness)
                
        return result 
    

    def draw_rec_for_materialview(self,img_form):
        result = img_form.copy()
        xy_list = []
        for val in self.yolo_detect_class_coordinate:
            for idx, coord in enumerate(val):
                x1 = coord[0]
                y1 = coord[1]
                x2 = coord[2]
                y2 = coord[3]
                
                if self.yolo_detect_class[idx] in self.xml_detection_partlist[self.current_index]:
                    cv2.rectangle(result, (int(x1.item()), int(y1.item())), (int(x2.item()), int(y2.item())), (255, 0, 0), 2)
                # print("x1 : {}, y1: {} x2: {} y2: {}".format(int(x1), int(y1)), (int(x2), int(y2)))
                    xy_list.append([int(x1.item()), int(y1.item()), int(x2.item()), int(y2.item())])
                if self.is_grabbing and self.object_grab_check(xy_list): # True ,False 반환 
                    grab_text = "Good."
                else:
                    grab_text = "Grab in red box !"
                # 객체의 크기를 이미지에 표시
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                font_scale2 = 1
                font_color2 = (255, 0 ,0)
                font_color3 = (0, 0, 255)
                font_thickness = 1
                font_thickness2 = 2
                
                font_color = (255, 255, 255)  # 흰색
                text_size, _ = cv2.getTextSize(self.yolo_detect_class[idx], font, font_scale, font_thickness)
                text_x = int((x1 + x2) / 2 - text_size[0] / 2)
                text_y = int(y2 + text_size[1] + 5)  # 객체 아래에 위치
                
                if self.yolo_detect_class[idx] in self.xml_detection_partlist[self.current_index]:
                    cv2.putText(result, self.yolo_detect_class[idx], (text_x, text_y), font, font_scale, font_color, font_thickness)
                    # cv2.putText(result, self.grab_status_text, (200, 50), font, font_scale, font_color2, font_thickness) #위치 수정 필요
                    cv2.putText(result, grab_text, (200, 50), font, font_scale2, font_color3, font_thickness2)           #위치 수정 필요
        return result 
        
        
        # YOLO 객체 감지
        #  for box in xyxy_bar:
        #     # 박스 좌표와 신뢰도 추출
        #     if len(box) >= 4:
        #         x1, y1, x2, y2 = box[:4]  # bounding box 좌표
            
        #         print("x1: {} y1: {} x2: {} y2: {}".format(int(x1), int(y1), int(x2), int(y2)))
                
        #         # 각 객체의 박스를 OpenCV 이미지에 그립니다.
        #         cv2.rectangle(img_form, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
            
    def measure_bar_size(self, xyxy_bar):
        result_size = 0
        if len(xyxy_bar) >= 4:
            # 박스 좌표 추출
            x1 = xyxy_bar[0]
            y1 = xyxy_bar[1]
            x2 = xyxy_bar[2]
            y2 = xyxy_bar[3]
            
            x1 = round(x1.item(), 2)
            y1 = round(y1.item(), 2)
            x2 = round(x2.item(), 2)
            y2 = round(y2.item(), 2)
            
            # 실제 길이와 픽셀 길이의 비율 계산
            pixel_length_wid = abs(x2 - x1)  # 픽셀 길이
            pixel_length_hei = abs(y2 - y1)
            
            if pixel_length_wid > pixel_length_hei:
                pixel_length_wid, pixel_length_hei = pixel_length_hei, pixel_length_wid
            if 80 < pixel_length_hei < 90:
                real_wid = 3
            else:
                real_wid = 2.5
            # real_length = 2  # 실제 길이 (여기서는 2cm)
            pixel_to_cm_ratio = real_wid / pixel_length_wid
            # 객체의 픽셀 좌표를 실제 길이로 변환
            real_x1 = x1 * pixel_to_cm_ratio
            real_x2 = x2 * pixel_to_cm_ratio
            real_y1 = y1 * pixel_to_cm_ratio
            real_y2 = y2 * pixel_to_cm_ratio
            
            # 객체의 크기 계산
            
            real_width = abs(real_x2 - real_x1)
            real_height = abs(real_y2 - real_y1)
            
            # real_width = round(real_width.item(), 2)
            # real_height = round(real_height.item(), 2)
            # 객체의 너비와 높이를 문자열로 변환
            
            size_text = "Width: {:.3f} cm, Height: {:.3f} cm".format(real_width, real_height)
            # print(size_text)
            
            if 3.00 <= real_height < 4.55:
                result_size = 1
            elif 4.55 <= real_height < 5.55:
                result_size = 2
            else:
                result_size = 3
        else:
            result_size = 0
        return result_size
            

    def set_yolochecklist(self, tmp_step):
        self.check_is_step_pass = [0] * len(self.xml_detection_partlist[tmp_step])
        
    def check_zero_index_yolocheck(self):
        for idx, val in enumerate(self.check_is_step_pass):
            if val == 0:
                return idx
        return -1

    def isyolomodel_pass(self):
        result = 0
        if self.xml_detection_countlist[self.current_index] == '0' : #count가 0이라서 detect 해야할 필요 없음
            result = 1
        else:
            if self.current_index == 0:
                for val in self.yolo_detect_class:
                    if val in self.xml_detection_partlist[0]:
                        try:
                            index = self.xml_detection_partlist[0].index(val)
                            self.check_is_step_pass[index] = 1
                        except ValueError:
                            pass
        
                if all(element == 1 for element in self.check_is_step_pass) :
                        result = 1
            # detected_cls = set(sorted(self.yolo_detect_class_workview))
            # must_be_detected_cls = set(sorted(self.xml_detection_partlist[self.current_index]))
            # if must_be_detected_cls == detected_cls :
            else:
                for val in self.yolo_detect_class_workview:
                    if val in self.xml_detection_partlist[self.current_index]:
                        try:
                            index = self.xml_detection_partlist[self.current_index].index(val)
                            self.check_is_step_pass[index] = 1
                        except ValueError:
                            pass
                
                if all(element == 1 for element in self.check_is_step_pass) :
                    if self.xml_detection_modellist[self.current_index] == '0':
                        result = 1
                    elif self.xml_detection_modellist[self.current_index] == '1':
                        if self.stepmodel_timecount == 50:
                            result = 1
                            self.stepmodel_timecount =0
                        else:
                            self.stepmodel_timecount += 1

        return result


    def load_media_files(self): # 폴더내 모든 파일 불러와서 숫자 순서 순으로 정렬 
        media_files = []
        try:
            tmp_listdir = os.listdir(self.media_folder)
        except FileNotFoundError:
            print(f"The directory '{self.media_folder}' does not exist.")

        for file_name in tmp_listdir:
            file_path = os.path.join(self.media_folder, file_name)
            if file_name.endswith('.jpg') or file_name.endswith('.png') or file_name.endswith('.avi'):
                media_files.append(file_path)
        media_files.sort(key=lambda x: int(os.path.basename(x).split('_')[0]))    
        return media_files

    def display_media(self): # 가이드 띄우기- 이미지/영상
        global inputID, name, workname, global_work_data 
        if self.current_index < len(self.media_files):
            media_file = self.media_files[self.current_index]
            if media_file.endswith('.jpg') or media_file.endswith('.png'):
                self.display_image(media_file)
                if TESTMODE == 1 :
                    self.current_index += 1
                elif TESTMODE == 0 :
                    if self.isyolomodel_pass() == 1:
                        self.current_index += 1
                        self.iscorrecttimer_on = 1
                        self.set_yolochecklist(self.current_index)
                        
                if self.current_index in [11, 17,20]:  # 11번째 사진, 17번째 사진의 경우
                    self.timer.start(5000)  # 5초 동안 표시
                else:
                    self.timer.start(200)  # 나머지는 0.5초 동안 표시
                #self.timer.start(5000)  # 이미지를 3초 동안 표시
            elif media_file.endswith('.avi'):
                self.display_video(media_file)
        elif self.current_index == len(self.media_files):
            self.timer.stop()
            self.checklist[41].setText('✔️')
            self.workorderLabel.setText("작업이 완료되었습니다.")
            self.startButton.show()
            self.quitButton.show()
        # 스크롤을 자동으로 아래로 내리는 코드 추가
        if self.current_index>1:
            scroll_bar = self.scrollArea_2.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.value() + 20)

    def display_image(self, image_file): #이미지 띄우기 
        
        pixmap = QPixmap(image_file)
        self.progresslist[self.current_index].setFont(self.fontNow)  
        ordernow=self.progresslist[self.current_index].text()
        self.workorderLabel.setText(ordernow)
        self.progresslist[self.current_index-1].setFont(self.fontOld)
        self.checklist[self.current_index-1].setFont(self.fontCheck)     
        self.checklist[self.current_index-1].setText('✔️')   
        self.progressBar.setValue(self.current_index+1)
        self.workGuideLabel.setPixmap(pixmap.scaled(self.workGuideLabel.size()))
        if self.current_index <= 41:
            self.checklist[41].setText('')

    def display_video(self, video_file): # 영상 띄우기 
        
        self.progresslist[self.current_index].setFont(self.fontNow)
        self.ordernow=self.progresslist[self.current_index].text()
        self.workorderLabel.setText(self.ordernow)
        self.progresslist[self.current_index-1].setFont(self.fontOld)

        self.checklist[self.current_index-1].setFont(self.fontCheck)     
        self.checklist[self.current_index-1].setText('✔️')   
        self.progressBar.setValue(self.current_index+1)
        
        cap = cv2.VideoCapture(video_file)
        fps = cap.get(cv2.CAP_PROP_FPS)  # 영상의 프레임 속도 가져오기
        
        while True:
            ret, frame = cap.read()
            if not ret:
                self.playback_count += 2
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
                #time.sleep(1 / fps)  # 프레임을 표시하는 간격만큼 대기  - 캠 킬때는 이거 뮤트하기 너무 느from PyQt5.QtWidgets import QMessageBox려짐       
        cap.release()
        
        self.current_index += 1  # 다음 미디어 파일로 이동
        self.playback_count = 0  # 재생 횟수 초기화
        self.timer.start(1000)  # 1초 후에 다음 미디어 파일을 표시
    
# --- workGuideLabel 띄우기 끝 
                
    def set_green_ok(self, tmpframe):
        result = tmpframe.copy()
        
        
        if self.iscorrecttimer_on == 1:
            if self.correcttimer == 30:
                self.iscorrecttimer_on = 0
                self.correcttimer =0

            else:
                self.correcttimer +=1
        

        # print("x1 : {}, y1: {} x2: {} y2: {}".format(int(x1), int(y1)), (int(x2), int(y2)))
        # 객체의 크기를 이미지에 표시
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2
        font_thickness = 1
        font_color = (0, 255, 0)  # 흰색
        org = (int(result.shape[1]/2) - 50, int(result.shape[0]/2)) 
        ok_str = "OK"
        
        if self.iscorrecttimer_on == 1 :
            cv2.putText(result, ok_str, org, font, font_scale, font_color, font_thickness)
        return result
    
    def show_step_timer(self, tmpframe):
        result = tmpframe.copy()
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2
        font_thickness = 1
        font_color = (255, 0, 0)  # 흰색
        org = (int(result.shape[1]/2) - 50, int(result.shape[0]/2)) 
        timer_str = str(self.stepmodel_timecount)
        
        if self.stepmodel_timecount != 0 :
            cv2.putText(result, timer_str, org, font, font_scale, font_color, font_thickness)
        return result
                
    
    def update_frame1(self):
        ret, frame_1 = cap1.read()  # 웹캠 1번
        if ret:
            frame_1 = cv2.rotate(frame_1, cv2.ROTATE_180)
            frame_1 = cv2.cvtColor(frame_1, cv2.COLOR_BGR2RGB)
            #frame_1으로 predict
            self.yolo_update_workview(frame_1)
            frame_1 = self.draw_rec(frame_1)
            frame_1 = self.set_green_ok(frame_1)
            frame_1 = self.show_step_timer(frame_1)
            #frame_1에다가 rectangle 그리기 
            height, width, channel = frame_1.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame_1.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap_1 = QPixmap.fromImage(q_img)
            self.workNowLabel.setPixmap(pixmap_1)

    def update_frame2(self):
        ret, frame_2 = cap2.read()  # 웹캠 2번
        if ret:
            frame_2 = cv2.cvtColor(frame_2, cv2.COLOR_BGR2RGB)
            self.mp_update(frame_2)
            self.yolo_update(frame_2)
            frame_2 = self.draw_rec_for_materialview(frame_2)
            height, width, channel = frame_2.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame_2.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap_2 = QPixmap.fromImage(q_img)
            self.materialLabel.setPixmap(pixmap_2)
                
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
            font = QFont(); font.setPointSize(12)
            tmp_txt = "{}. ".format(idx+1) +val 
            self.progresslist[idx].setFont(font)
            self.progresslist[idx].setText(tmp_txt)
                    
    def go_main(self):
        if self.current_index == len(self.media_files): # 작업 완료 됐는데 버튼을 눌렀을 때만 경고 팝업 창 표시
            QMessageBox.warning(self,'경고','작업 종료나 재시작 버튼을 먼저 눌러주세요.')
        else:
            self.hide()
            main_window = self.parent  # 메인 창을 찾음
            main_window.get_currentoperator(0)  # 로그아웃한 상태로 설정
            main_window.show()
             
    def go_back(self):
        if self.current_index == len(self.media_files): # 작업 완료 됐는데 버튼을 눌렀을 때만 경고 팝업 창 표시
            QMessageBox.warning(self,'경고','작업 종료나 재시작 버튼을 먼저 눌러주세요.')
        else:
            retval =QMessageBox.question(self, 'Back', '작업선택창으로 이동하시겠습니까?', QMessageBox.Yes|QMessageBox.No, QMessageBox.Yes)
            if retval == QMessageBox.Yes:# 뒤로 가기 동작 수행
                self.hide()
                global inputID 
                selectPage = selectWindow(parent=self.parent)
                selectPage.get_currentoperator(inputID)
                selectPage.show()                   
            
       


    def go_error(self):
        if self.current_index == len(self.media_files): # 작업 완료 됐는데 버튼을 눌렀을 때만 경고 팝업 창 표시
            QMessageBox.warning(self,'경고','작업 종료나 재시작 버튼을 먼저 눌러주세요.')
        else:
            global errorpart 
            errorpart = self.workorderLabel.text()
            self.hide()
            error_window = errorWindow(parent=self.parent)  # 에러 페이지를 열고
            error_window.show()  # 에러 페이지를 보여줌          
         
        
class errorWindow(QMainWindow,form_errorwindowpage_ui):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.parent = parent 
        global inputID, name, workname,errorpart
        self.idLabel.setText(str(inputID))
        self.nameLabel.setText(name)  
        self.worknameLabel.setText(workname)
        self.errorpartLabel.setText(errorpart)
        
        self.saveButton.clicked.connect(self.report_error)
        self.operatorList = self.get_operatorList()
        self.backButton.clicked.connect(self.go_back)

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
        self.close() #현재 화면 숨겨주고
        global inputID
        assemblyPage = assemblyWindow(parent=self.parent) #페이지 3 불러오고
        assemblyPage.get_currentoperator(inputID)
        assemblyPage.show()
        
    def report_error(self): #에러나면 어디로 가지? 일단 뒤로 
        global errorReason, inputID, name, workname, errorpart, global_error_data, global_work_data
        errorReason = self.reasonTextEdit.toPlainText() 
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        errorment='불량'
        
        db = Cdatabase_connect()
        error_work_report=pd.DataFrame({'작업명': [workname],' ID ': [inputID], '작업자': [name], ' 작업 날짜 ':[formatted_time] ,'작업 상태': [errorment]})
        db.insert_workdata(workname,inputID,name,formatted_time,errorment)
        #global_work_data = pd.concat([global_work_data, error_work_report], ignore_index=True)
        
        
        error_report = pd.DataFrame({'작업명': [workname],'ID': [inputID], '작업자': [name], '작업 날짜':[formatted_time] ,'불량 단계': [errorpart], '불량 사유': [errorReason]})
        db.insert_errordata(workname,inputID,name,formatted_time,errorpart,errorReason)
        #global_error_data = pd.concat([global_error_data, error_report], ignore_index=True)      
        db.dbclose()
        
        self.close() 
        assemblyPage = assemblyWindow(parent=self.parent) #페이지 3 불러오고
        assemblyPage.get_currentoperator(inputID)
        assemblyPage.show()          
        

    def get_currentoperator(self,id):
        self.currentOperator = id

class statisticWindow(QMainWindow,form_statisticpage_ui):

    def __init__(self, parent):
        global global_work_data, global_error_data
        db = Cdatabase_connect() 
        workdata=db.get_workdatas()
        global_work_data=pd.DataFrame(workdata,columns=['작업명',' ID ', '작업자',  ' 작업 날짜 ','작업 상태']) 
        
        errordata=db.get_errordata()
        global_error_data=pd.DataFrame(errordata, columns=["작업명", "ID", "작업자", "작업 날짜", "불량 단계", "불량 사유"])
        db.dbclose()
        
        super().__init__(parent)
        global inputID, name 
        self.parent = parent
        self.setupUi(self)
        self.logoutButton.clicked.connect(self.go_main)
        self.backButton.clicked.connect(self.go_back)
        self.errorButton.clicked.connect(self.showError)
        self.operatorList = self.get_operatorList()
        self.parent = parent
        self.idLabel.setText(str(inputID))
        self.nameLabel.setText(name)        
        self.errorTable.hide()
        # 그래프를 표시할 위젯 추가
        self.graphWidget = QWidget()
        self.graphLayout = QVBoxLayout()
        self.graphWidget.setLayout(self.graphLayout)
        self.taskgraphLayout.addWidget(self.graphWidget)

        self.graphWidget2 = QWidget()
        self.graphLayout2 = QVBoxLayout()
        self.graphWidget2.setLayout(self.graphLayout2)
        self.workergraphLayout.addWidget(self.graphWidget2)
        
        # 작업명 콤보박스에서 작업명을 선택했을 때 그래프 표시
        self.personCombobox.addItems(global_work_data['작업자'].unique())
        self.workCombobox.currentIndexChanged.connect(self.showTaskGraph)
        self.personCombobox.currentIndexChanged.connect(self.showPersonGraph)
        # 그래프 초기화
        self.current_graph = None
        self.current_graph2 = None
        # 생성자에서 그래프 표시
        self.showTaskGraph()
        self.showPersonGraph()
        
        
    def showPersonGraph(self):
        global global_work_data
        selected_person = self.personCombobox.currentText()
        selected_work = self.workCombobox.currentText()
        filter_data=global_work_data[global_work_data['작업명'] == selected_work]
        filtered_data = filter_data[filter_data['작업자'] == selected_person]

        # 작업명 별 작업 상태 데이터 분석
        pivot_data = pd.pivot_table(filtered_data, index='작업명', columns='작업 상태', aggfunc='size', fill_value=0)
    # 작업 상태가 없으면 빈 데이터프레임을 생성하여 플로팅 에러를 방지
        if '완료' not in pivot_data.columns:
            pivot_data['완료'] = 0
        if '불량' not in pivot_data.columns:
            pivot_data['불량'] = 0
        fig, ax = plt.subplots()
        bar_width = 0.35  # 막대 너비
        index = np.arange(len(pivot_data.index))  # x축 인덱스

        # '완료' 막대 그리기
        rects1 = ax.bar(index, pivot_data['완료'], bar_width, label='완료')

        # '불량' 막대 그리기
        rects2 = ax.bar(index + bar_width, pivot_data['불량'], bar_width, label='불량')

        ax.set_ylabel('작업 개수', rotation=90)
        ax.set_xlabel('작업 명', rotation=0)
        ax.set_title(f'작업자 {selected_person}의 작업 별 작업 상태')
        ax.set_xticks(index + bar_width / 2)
        ax.set_xticklabels(pivot_data.index)
        ax.legend()

        # 막대 위에 개수 표시
        for rects in [rects1, rects2]:
            for rect in rects:
                height = rect.get_height()
                ax.annotate('{}'.format(height),
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')

        # 이전 그래프를 지우고 새로운 그래프를 표시
        if self.current_graph2 is not None:
            self.graphLayout2.removeWidget(self.current_graph2)
            self.current_graph2.deleteLater()

        # Matplotlib 그래프를 PyQt 위젯으로 변환하여 표시
        canvas = FigureCanvas(fig)
        self.graphLayout2.addWidget(canvas)
        self.current_graph2 = canvas
        
    def showTaskGraph(self):
        global global_work_data

        selected_work = self.workCombobox.currentText()
        filtered_data = global_work_data[global_work_data['작업명'] == selected_work]

        # 작업 상태에 따른 데이터 분석 및 그래프 생성
        status_counts = filtered_data['작업 상태'].value_counts()
        labels = status_counts.index
        sizes = status_counts.values

        # 불량과 완료의 개수 계산
        num_defective = status_counts.get('불량', 0)
        num_completed = status_counts.get('완료', 0)
        total_count = len(filtered_data)

        # 원형 그래프 생성
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax.set_title(selected_work)

        # 그래프 옆에 작업 상태별 작업 개수 및 총 작업 개수 표시
        text = f'불량: {num_defective}개, 완료: {num_completed}개\n총 작업 개수: {total_count}개'
        self.label.setText(text) 
        # 이전 그래프를 지우고 새로운 그래프를 표시
        if self.current_graph is not None:
            self.graphLayout.removeWidget(self.current_graph)
            self.current_graph.deleteLater()

        # Matplotlib 그래프를 PyQt 위젯으로 변환하여 표시
        canvas = FigureCanvas(fig)
        self.graphLayout.addWidget(canvas)

        # 현재 그래프 저장
        self.current_graph = canvas         
        
        
    def showEvent(self,event):
        super().showEvent(event)
        global global_work_data

        # workTable에 데이터프레임 표시
        self.workTable.setRowCount(len(global_work_data.index))
        self.workTable.setColumnCount(len(global_work_data.columns))
        self.workTable.setHorizontalHeaderLabels(global_work_data.columns)

        for i in range(len(global_work_data.index)):
            for j in range(len(global_work_data.columns)):
                item = QTableWidgetItem(str(global_work_data.iloc[i, j]))
                if j == 4 and global_work_data.columns[j] == '작업 상태' and global_work_data.iloc[i, j] == '불량':
                    item.setForeground(QColor('red'))  # 빨간색 글자로 설정
                self.workTable.setItem(i, j, item)
        self.workTable.resizeColumnsToContents()
        self.workTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        
    def showError(self):
        global global_error_data

        # errorTable에 데이터프레임 표시
        self.errorTable.setRowCount(len(global_error_data.index))
        self.errorTable.setColumnCount(len(global_error_data.columns))
        self.errorTable.setHorizontalHeaderLabels(global_error_data.columns)

        for i in range(len(global_error_data.index)):
            for j in range(len(global_error_data.columns)):
                item = QTableWidgetItem(str(global_error_data.iloc[i, j]))
                self.errorTable.setItem(i, j, item)
        self.errorTable.resizeColumnsToContents()
        self.errorTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.errorTable.show()


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
        main_window = self.parent  # 메인 창을 찾음
        main_window.get_currentoperator(0)  # 로그아웃한 상태로 설정
        main_window.show()

    def go_back(self):
        self.hide()
        global inputID 
        selectPage = selectWindow(parent=self.parent) #페이지 2로 불러오고
        selectPage.get_currentoperator(inputID)
        selectPage.show() 

class servicenotreadyWindow(QMainWindow,form_servicenotready_ui):

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.backButton.clicked.connect(self.go_back)
        global inputID, name 
        self.parent = parent
        
    def go_back(self):
        self.hide()
        global inputID 
        selectPage = selectWindow(parent=self.parent) #페이지 2로 불러오고
        selectPage.get_currentoperator(inputID)
        selectPage.show() 


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    atexit.register(cleanup)
    sys.exit(app.exec())