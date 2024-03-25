## ui 구성 - 5페이지 : 로그인창, 작업선택창, 작업창,불량보고창, 통계확인창 
### 1.로그인창 - "loginWindow.ui"
![login](https://github.com/addinedu-ros-4th/deeplearning-repo-1/assets/162243509/f6926a99-2e61-4f9a-b973-f949000ace9f)
#### login 라벨 hide하다가 IDinput에 사용자가 id입력하고 loginButton 누르면 해당 id 넣은 로그인 문구 띄워지며 작업선택창으로 이동 

### 2.작업선택창 - "selectWindow.ui"
![select](https://github.com/addinedu-ros-4th/deeplearning-repo-1/assets/162243509/96c9aaa6-de55-45d1-bd1d-d87c9f3351cb)
* 작업 선택하기: 6개의 버튼 중 하나 눌러 작업창 이동 ex) **selectDogButton**(후아유 강아지 조명 만들기) 누르면 후아유 강아지 조명 작업창으로 이동 
* 작업통계 확인하기 : **checkStatisticButton** 누르면 통계창으로 이동 
### 3.작업창 - "assemblyWindow.ui"
![assembly](https://github.com/addinedu-ros-4th/deeplearning-repo-1/assets/162243509/fdd38984-b9e7-4180-940c-cb724ada27eb)
* **backButton** - 누르면 작업선택창으로 이동
* **idLabel** - 로그인창에서 사용자가 입력했던 id 받아오고/db에서 해당 id와 매칭되는 작업자명 연동해 nameLabel에 띄움 ex)id 0001 -김ㅇㅇ
* **logoutButton** - 받아왔던 id 날라가고 로그인창으로 이동
* **progress_num & check_num** -  일단 단계 15개 만들어두긴했는데 단계 개수 생각해봐야할듯 - db에서 작업단계 받아와서 띄우기 
  * **progress1~progress15**: 각 단계별 과정이 나타나있음/ 현재 진행중인 단계에서는 글자를 강조함(크기,bold)
  * **check1~check15**: 각 단계의 완료 여부 표시 - 완료된 단계에서는 체크✔️표시
* **errorButton** - 불량보고 버튼: 누르면 불량보고창으로 이동 
* **workGuideLabel**: 각 단계별로 작업자가 해야할 작업의 이미지를 보여줘 가이드  
* **workNowLabel** : 현재 작업중인 모습 비추는 웹캠 송출  
* **materialLabel** : 재료창 비추는 웹캠 송출  
* **progressBar** : 작업 진행 상황을 상태창으로 보여줌 - (진행완료된 작업단계수/전체 작업단계수) * 100 %
  
### 4.불량보고창 - "errorWindow.ui"
![error](https://github.com/addinedu-ros-4th/deeplearning-repo-1/assets/162243509/ec6a4721-5b4f-4a9b-9550-951abba87afa)
* **idLabel/nameLabel/workNameLabel/errorPartLabel**-id,작업자,작업명,불량 단계는 작업창에서 받은 정보 그대로 가져옴
  * ex) id 0001 김ㅇㅇ이 후아유 강아지 조명 만들기 하다가 2단계 block B를 가져오세요에서 불량보고버튼 누름
  * -> id:0001, 작업자:김ㅇㅇ, 작업명:후아유 강아지 조명, 불량 단계: 2단계 block B를 가져오세요
* **reasonTextEdit** - 작업자가 불량 사유 입력하도록 함
* **saveButton** - 불량 사유 다 입력했으면 저장 -> 불량 보고서에 "id,작업자,작업명,불량 단계,불량사유" 저장됨 -> df로 만들어서 저장해두는게 좋을듯  

### 5.통계창 - "statisticWindow.ui"
![statistic](https://github.com/addinedu-ros-4th/deeplearning-repo-1/assets/162243509/b5e7b428-c7c4-4f9e-b5b2-3e1d2c7bf089)
* **backButton** - 누르면 작업선택창으로 이동
* **idLabel** - 로그인창에서 사용자가 입력했던 id 받아오고/db에서 해당 id와 매칭되는 작업자명 연동해 nameLabel에 띄움 ex)id 0001 -김ㅇㅇ
* **logoutButton** - 받아왔던 id 날라가고 로그인창으로 이동
* **taskTable** - 작업이 진행되었던 내역 list 출력 - 작업명,id,작업자,작업날짜,작업상태 뜸 - 작업상태-**불량**이면 해당 글자 강조하기
* **errorButton** - 불량 보고서 확인 버튼 누르면 불량 보고창에서 입력했던 불량 보고가 출력됨 작업명, 불량단계, ID, 작업자, 작업날짜, 불량사유 df에서 불러오기
* **taskStatisticButton** - 작업별 통계 확인 버튼 누르면 작업별 통계가 **taskgraphLayout**에 출력됨 
* **taskgraphLayout** - matplotlib로 그래프 그린거 이 창에 띄우기(그래프 그리는 건 파이썬에서 완료하고 띄우기만) - 참고할 블로그:  https://m.blog.naver.com/hjinha2/221839259540
* **workerStatisticButton** - 작업자별 통계 확인 버튼 누르면 작업자별 통계가 **workergraphLayout**에 출력됨
* **workergraphLayout** - **taskgraphLayout**와 같은 시스템으로 matplotlib 출력 
 



## workingorder.xml
---
  이 파일은 프로젝트의 작업 순서가 들어 가있는 파일이다
  
  ![image](https://github.com/dyjung-dev/Amr_eda_basic/assets/137265648/47c41332-3af7-4e55-b132-708a40b475c9)
  
  위의 이미지는 내부 구조 예시이다.
  
  새로운 작업 목록을 작성할 경우 위의 파일을 복사해서 새로운 파일을 작성한뒤,    
  ```<package name="dog_light">```에서 "dog_light"를 해당 작업으로 수정한뒤 작업 목록을 작성한다   
  
  예) ```<package name="watch">``` 로 수정하고 "watch"의 작업 순서롤 작성해준다    

## read_xml.py
---
  클래스 Cxml_reader이 들어 있는 파일이다 

  * Cxml_reader(path,workingname) : 클래스 생성자
       
    * Parameter
        
      | parameter | description |
      |---|---|
      |path|읽고자 하는 xml 파일의 경로|
      |workingname|xml 파일 안에 정의되어 있는 작업 이름|

    * Return
      | return | description |
      |---|---|
      | Cxml_reader | Cxml_reader 클래스를 반환한다|
      
  * xml_open() : 생성할때 입력한 경로에 있는 xml을 불러온다
                 생성자 안에서 호출된다
    
  * get_order_count() : 작업 순서의 목록 갯수를 반환하는 함수

   * get_order_list() : 작업 목록을 리스트 형식으로 반환하는 함수
     
## test_use_xmlreader.py
---
Cxml_reader 클래스 사용 예제가 들어 있는 파일이다

![image](https://github.com/dyjung-dev/Amr_eda_basic/assets/137265648/2379e795-cb86-43d1-ab0f-66b78021c91a)
