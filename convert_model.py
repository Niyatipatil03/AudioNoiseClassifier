import torch
import torch.nn as nn
import numpy as np
  
# Define the exact same model architecture from your classifier.py
class AudioCNN(nn.Module):
    def __init__(self):
      super(AudioCNN, self).__init__()
      self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1)
      self.pool = nn.MaxPool2d(kernel_size=2, stride=2, padding=0)
      self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
      self.fc1 = nn.Linear(32 * 16 * 16, 128) # Adjust these numbers to match your model
      self.fc2 = nn.Linear(128, 2)
   
    def forward(self, x):
      x = self.pool(torch.relu(self.conv1(x)))
      x = self.pool(torch.relu(self.conv2(x)))
      x = x.view(-1, 32 * 16 * 16)
      x = torch.relu(self.fc1(x))
      x = self.fc2(x)
    return x
   
    # 1. Load the model
model = AudioCNN()
model.load_state_dict(torch.load('audio_model.pth', map_location='cpu'))
model.eval()
   
    # 2. Export to ONNX (Intermediate step)
dummy_input = torch.randn(1, 1, 64, 64) # Adjust size to match your input
torch.onnx.export(model, dummy_input, "model.onnx")

print("Model successfully converted to ONNX!")
