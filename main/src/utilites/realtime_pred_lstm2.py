import cv2
import torch
import numpy as np
import mediapipe as mp
from model import SkeletonLSTM  # 모델이 정의된 모듈을 import 합니다.

# 모델 경로
model_path = "/home/bo/amr_ws/dl_project/model/skeleton_lstm_model.pth"

# 모델 초기화 및 로드
model = SkeletonLSTM()
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))  # 모델을 CPU로 로드합니다.
model.eval()  # 모델을 평가 모드로 설정합니다.

# 손 감지 모듈 초기화
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

def detect_hand_landmarks(image):
    # 이미지를 RGB로 변환
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 손 감지 수행
    results = hands.process(image_rgb)

    # 감지된 손이 없는 경우
    if not results.multi_hand_landmarks:
        return None

    # 손의 좌표 추출
    landmarks = results.multi_hand_landmarks[0].landmark

    # 각 랜드마크의 x, y 좌표를 추출하여 리스트에 저장
    landmark_coords = []
    for landmark in landmarks:
        landmark_coords.append(landmark.x)
        landmark_coords.append(landmark.y)

    return landmark_coords

# 웹캠 열기
cap = cv2.VideoCapture(0)

frame_sequence = []  # 시퀀스를 저장할 리스트 초기화

# 모델의 입력 크기 설정
input_size = 10

while True:
    ret, frame = cap.read()  # 웹캠에서 프레임 읽기

    # 손의 좌표 감지 및 시퀀스에 추가
    hand_coords = detect_hand_landmarks(frame)
    if hand_coords:
        frame_sequence.append(hand_coords)

        # 시퀀스의 길이가 모델의 입력 크기와 같으면
        if len(frame_sequence) == input_size:
            # 리스트를 텐서로 변환하여 모델에 입력
            inputs = torch.Tensor([frame_sequence])  # 배치 차원 추가

            # 모델로 추론 수행
            outputs = model(inputs)

            # 결과 출력
            output_value = outputs[0][0].item()
            if output_value < 0:
                    message = "release"
            else:
                message = "grab"
            # 시퀀스 초기화
            frame_sequence = []
            cv2.putText(frame, message, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # 화면에 프레임 표시
    cv2.imshow('Frame', frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 종료
cap.release()
cv2.destroyAllWindows()
