import os
import sys
import time 
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *

def resource_path(relative_path):  # ui 파일 가져오는 함수. 
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

form_1 = resource_path('loginWindow.ui') 
form_class_1 = uic.loadUiType(form_1)[0]
form_2 = resource_path('selectWindow.ui')
form_class_2 = uic.loadUiType(form_2)[0]
form_3 = resource_path('assemblyWindow.ui')
form_class_3 = uic.loadUiType(form_3)[0] 
form_4= resource_path('errorWindow.ui') 
form_class_4 = uic.loadUiType(form_4)[0] 
form_5= resource_path('statisticWindow.ui') 
form_class_5 = uic.loadUiType(form_5)[0]  

class MainWindow(QMainWindow, form_class_1):
    def __init__(self):
        super().__init__()
        self.setupUi(self) 
        self.loginButton.clicked.connect(self.get_login)
        
    def get_login(self): ## 로그인 버튼 클릭 - 로그인 정보 저장 & 선택 화면으로 넘어가기 
        #로그인 정보 여기는 db연동 후 작업해야할듯 
        input = self.IDinput.toPlainText()
        self.IDinput.clear()
        self.login.setText("ID %s 작업자 %s님 작업장으로 로그인 합니다"%(input,'김ㅇㅇ')) #김ㅇㅇ은 db에서 받아와야함 
        
         #선택화면으로 이동 
        self.hide() #현재 화면 숨겨주고
        selectPage = selectWindow(self) #페이지 2로 불러오고
        selectPage.show()        
        

class selectWindow(QMainWindow,form_class_2):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        
        self.selectDogButton.clicked.connect(self.go_assembly)
        self.selectdeskButton.clicked.connect(self.go_assembly)
        self.selectToyButton.clicked.connect(self.go_assembly)
        self.selectTableButton.clicked.connect(self.go_assembly)
        self.selectChairButton.clicked.connect(self.go_assembly)
        self.selectEtcButton.clicked.connect(self.go_assembly)
        
        self.checkStatisticButton.clicked.connect(self.go_statistic)
        
    def go_assembly(self): #작업창 이동 
        self.hide() #현재 화면 숨겨주고
        assemblyPage = assemblyWindow(self) #페이지 3 불러오고
        assemblyPage.show()       
        
    def go_statistic(self): #통계페이지로 이동 
        self.hide() #현재 화면 숨겨주고
        statisticPage = statisticWindow(self) #페이지 4 불러오고
        statisticPage.show()  
        
        
class assemblyWindow(QMainWindow,form_class_3):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self) 
        
        self.logoutButton.clicked.connect(self.go_main)
        self.backButton.clicked.connect(self.go_back)
        self.errorButton.clicked.connect(self.go_error)
        
    def go_main(self):
        self.hide()
        self.parent().parent().show()
           
    def go_back(self):
        self.hide() #현재 화면 숨겨주고
        self.parent().show() #작업페이지로 감 

    def go_error(self):
        self.hide() #현재 화면 숨겨주고
        errorPage = errorWindow(self) #에러 페이지 불러오고
        errorPage.show()          
        
class errorWindow(QMainWindow,form_class_4):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.saveButton.clicked.connect(self.report_error)
    
    def report_error(self): #에러나면 어디로 가지? 일단 뒤로 
        self.hide() #현재 화면 숨겨주고
        self.parent().show() #작업페이지로 감 
       
class statisticWindow(QMainWindow,form_class_5):
   
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.logoutButton.clicked.connect(self.go_main)
        self.backButton.clicked.connect(self.go_back)

    def go_main(self): #메인 이동 
        self.hide()
        self.parent().parent().show()
           
    def go_back(self):
        self.hide() #현재 화면 숨겨주고
        self.parent().show() #작업페이지로 감 


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
