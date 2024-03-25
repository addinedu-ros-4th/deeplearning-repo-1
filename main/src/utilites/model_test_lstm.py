#모델의 가중치가 올바른 출력을 내는지 확인

import torch
import numpy as np
from model import SkeletonLSTM  # 모델이 정의된 모듈을 import 합니다.

# 모델 경로
model_path = "/home/bo/amr_ws/dl_project/model/skeleton_lstm_model.pth"

# 평가용 데이터셋과 정답 데이터셋을 준비합니다. (예시)
eval_inputs = torch.randn(100, 10, 42)  # 입력 데이터셋 (100개의 시퀀스, 각 시퀀스는 10개의 프레임, 각 프레임은 42개의 특징)
eval_labels = torch.randint(0, 2, (100,))  # 정답 데이터셋 (100개의 시퀀스에 대한 정답, 이진 분류를 가정)

# 모델을 평가 모드로 설정합니다.
model = SkeletonLSTM()
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))  # 모델을 CPU로 로드합니
model.eval()

# 평가 데이터셋에 대한 예측을 생성합니다.
with torch.no_grad():
    outputs = model(eval_inputs)

# 모델의 예측값을 기반으로 정확도를 계산합니다.
predictions = torch.argmax(outputs, dim=1)  # 각 시퀀스에 대한 예측값을 생성합니다.
accuracy = (predictions == eval_labels).float().mean().item()  # 정확하게 예측된 비율을 계산합니다.
print(f"Accuracy: {accuracy}")
