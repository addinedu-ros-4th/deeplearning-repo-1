import cv2
import torch
import numpy as np
import mediapipe as mp
from model import SkeletonLSTM  # 모델이 정의된 모듈을 import 합니다.

# 모델 경로
model_path = "/home/bo/amr_ws/dl_project/model/skeleton_lstm_model.pth"

# 모델 초기화
model = SkeletonLSTM()

# 모델 로드
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))  # 모델을 CPU로 로드합니다.
model.eval()  # 모델을 평가 모드로 설정합니다.

# 웹캠 열기
cap = cv2.VideoCapture(0)

# Mediapipe 손 감지 모듈 초기화
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# 이미지 프레임 시퀀스를 저장할 리스트 초기화
# 이미지 프레임 시퀀스를 저장할 리스트 초기화
frame_sequence = []

while True:
    ret, frame = cap.read()  # 웹캠에서 프레임 읽기
    
    if not ret:
        print("Failed to capture frame from webcam.")
        break

    # 손 감지
    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    if results.multi_hand_landmarks:
        # 손의 랜드마크를 이미지에 그리기
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # 손의 랜드마크 좌표를 시퀀스에 추가
            landmark_sequence = [landmark.x for landmark in hand_landmarks.landmark]
            frame_sequence.append(landmark_sequence)

            # 시퀀스의 길이가 모델의 입력 길이와 동일하면 모델에 입력 후 예측
            if len(frame_sequence) == model.input_size:
                # 시퀀스를 텐서로 변환하여 모델에 입력
                inputs = torch.tensor(frame_sequence, dtype=torch.float32).unsqueeze(0)  # 배치 차원 추가
                outputs = model(inputs)

                # 결과 출력
                print("Model Prediction:", outputs)

                # 시퀀스 초기화
                frame_sequence = []

    # 화면에 프레임 표시
    cv2.imshow('Frame', frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 종료
cap.release()
cv2.destroyAllWindows()
