# 작업 부품 구분 및 표시로 작업 시퀀스 학습을 도와 주는 서비스
![표지](https://github.com/seungyeonSeok/iot-/assets/162243509/dab70132-4d61-4a24-899d-131664cc8821)
#### 여기에 우리 시연영상 중 잘나온 부분 gif로 첨부하면 좋을듯 
## 1. 프로젝트 개요 
### 프로젝트 목표: ? 
#### - 팀명: daYeonbOsunhaLinseungyeOn 
#### - 팀원: 정다연(팀장), 김보선,  장하린, 석승연 

## 시스템 구성도 
![시스템구성도](https://github.com/seungyeonSeok/iot-/assets/162243509/3dfe0ec2-f7ec-4b34-bc80-a64388352019)
## 시퀸스 다이어그램 
![image](https://github.com/addinedu-ros-4th/deeplearning-repo-1/assets/162243509/3316c1cc-78d1-4338-8b34-93f7d95f341b)
## 기능리스트 
|구분|기능명|기능|
|---|---|---|
|객체탐지| **재료 구분-종류** |키트에 들어 있는 나무 블럭 15개, 종류가 다른 볼트 3쌍, 너트 1쌍을 모양에 따라 구분  |
|객체탐지| **재료 구분-크기** |모양이 비슷한 재료의 경우 사이즈 측정을 통해 재료를 2차 분류 bar블럭을 사이즈별 3종류로 구분 |
|작업자 상호작용| **grab/release 인식** |자재를 잡았을 때의 상태인 grab 상태와 자재를 놓았을 때의 상태인 release 상태 확인 |
|작업자 상호작용| **잘못된 자재 선택시 경고** |요구되는 자재가 아닌 다른 자재 근처에서 작업자의 grab하는 상태가 확인되면 경고 문구 도출 |
|데이터관리| **작업자 데이터 호출** |로그인시 입력된 ID가 db내 operator 테이블에 존재시 그 ID에 해당하는 작업자의 이름을 불러옴 |
|데이터관리| **작업 결과 저장** |db내 Workdata 테이블에 [작업명/ID/작업자 이름/작업날짜/작업상태(완료/불량)] 저장 |
|데이터관리| **불량보고 데이터 저장** |db내 errordata 테이블에 [작업명/ID/작업자 이름/작업날짜/불량 파트/불량 사유] 저장 |
|데이터관리| **작업 데이터 로드** |프로그램의 확장성을 위해 작업 데이터를 외부 xml 파일에서 로드함 |

## 적용 기술 

## 사용자 인터페이스 

## 시연 영상(링크)

## 발표 자료 

