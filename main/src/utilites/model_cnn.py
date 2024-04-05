import torch
import torch.nn as nn
import torch.nn.functional as F

# 모델 구조 정의
class cnn_HandGestureModel(nn.Module):
    def __init__(self):
        super(cnn_HandGestureModel, self).__init__()
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(42, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, 1)

    def forward(self, x):
        x = self.flatten(x)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = F.relu(self.fc2(x))
        x = F.dropout(x, training=self.training)
        x = torch.sigmoid(self.fc3(x))
        return x


