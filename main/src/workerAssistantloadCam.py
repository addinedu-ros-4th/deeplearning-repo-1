import os
import sys
import time 
import cv2
import numpy as np 
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from read_xml import Cxml_reader
from connect_database import Cdatabase_connect


form_loginpage_ui = uic.loadUiType("loginWindow.ui")[0]
form_selectpage_ui = uic.loadUiType("selectWindow.ui")[0]
form_assemblypage_ui = uic.loadUiType("assemblyWindow.ui")[0]
form_errorwindowpage_ui = uic.loadUiType("errorWindow.ui")[0]
form_statisticpage_ui = uic.loadUiType("statisticWindow.ui")[0]
form_servicenotready_ui = uic.loadUiType("serviceNotReady.ui")[0]

inputID=''; name='' ; #사용자 정보 

# 웹캠 속성 설정
cap1 = cv2.VideoCapture(1)
cap2 = cv2.VideoCapture(2)        
        
cap1.set(cv2.CAP_PROP_FPS, 30)
cap2.set(cv2.CAP_PROP_FPS, 30)
        
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

        self.progresslist = [self.progress1, self.progress2, self.progress3, self.progress4, self.progress5,
                             self.progress6, self.progress7, self.progress8, self.progress9, self.progress10,
                             self.progress11, self.progress12, self.progress13, self.progress14, self.progress15,
                             self.progress16, self.progress17, self.progress18, self.progress19, self.progress20,
                             self.progress21, self.progress22, self.progress23, self.progress24, self.progress25,]
        self.checklist = [self.check_1,self.check_2,self.check_3,self.check_4,self.check_5,
                          self.check_6,self.check_7,self.check_8,self.check_9,self.check_10,
                          self.check_11,self.check_12,self.check_13,self.check_14,self.check_15,
                          self.check_16,self.check_17,self.check_18,self.check_19,self.check_20,
                          self.check_21,self.check_22,self.check_23,self.check_24,self.check_25]
        cxml = Cxml_reader("workingorder.xml", "dog_light")  #xml_reader 클래스를 생성한다. 생성시 불러올 xml 주소를 인자로 넘겨준다
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

    def update_frame1(self):
        ret, frame = cap1.read()  # 웹캠 1번
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.workNowLabel.setPixmap(pixmap)

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
            self.progresslist[idx].setMargin(7)
            self.checklist[idx].setMargin(6)
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
        self.idLabel.setText(inputID)
        self.nameLabel.setText(name)  
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
