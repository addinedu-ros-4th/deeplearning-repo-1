import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model

# 저장된 모델 불러오기
model = load_model("/home/bo/amr_ws/dl_project/model/model_mlp_grab_vector.h5")

# 마디아 파이프 라이브러리의 Hand 모델을 로드합니다.
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.3)

# 웹캠에서 비디오 스트림을 가져옵니다.
cap = cv2.VideoCapture(0)

# grab 상태를 저장하는 변수
is_grabbing = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 마디어 파이프에 프레임을 전달하여 랜드마크를 감지합니다.
    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # 랜드마크를 감지하고 표시합니다.
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
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
            prediction = model.predict(np.array([finger_vectors]))
            probability = prediction[0][0]  # 확률 값

            # grab 상태 결정
            is_grabbing = probability >= 0.3

            # grab 상태에 따라 텍스트를 추가합니다.
            status_text = f"Grab (Probability: {probability:.2f})" if is_grabbing else f"Release (Probability: {1 - probability:.2f})"
            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # 프레임을 화면에 출력합니다.
    cv2.imshow('Real-time Grab/Release Detection', frame)

    # 'q'를 누르면 종료합니다.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 웹캠 해제 및 창 닫기
cap.release()
cv2.destroyAllWindows()
