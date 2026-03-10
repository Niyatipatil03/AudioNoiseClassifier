import torch
import torch.nn as nn
import numpy as np
    
     # This is the exact architecture from your classifier.py
class AudioCNN(nn.Module):
  def __init__(self):
    super(AudioCNN, self).__init__()
    self.conv = nn.Sequential(
        nn.Conv2d(1, 16, 3, padding=1), nn.BatchNorm2d(16), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(16, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(), nn.MaxPool2d(2)
        )
        self.fc = nn.Sequential(
          nn.Flatten(),
          nn.Linear(128 * 8 * 4, 128), nn.ReLU(), nn.Dropout(0.4),
          nn.Linear(128, 2)
        )
    def forward(self, x):return self.fc(self.conv(x))
   
    # Load the PyTorch model
model = AudioCNN()
try:
  model.load_state_dict(torch.load('audio_model.pth', map_location='cpu'))
  model.eval()
   
        # Export to ONNX (Mobile format step 1)
  dummy_input = torch.randn(1, 1, 128, 64)
  torch.onnx.export(model, dummy_input, "model.onnx", opset_version=12)
  print("Successfully converted model to ONNX format.")
except Exception as e:
  print(f"Error during conversion: {e}")
