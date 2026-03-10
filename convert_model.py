import torch
import torch.nn as nn
import numpy as np
import onnx
from onnx_tf.backend import prepare
import tensorflow as tf

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

    def forward(self, x):
        return self.fc(self.conv(x))


# 1. Load PyTorch model
model = AudioCNN()
model.load_state_dict(torch.load("audio_model.pth", map_location="cpu"))
model.eval()

# 2. Convert to ONNX
dummy_input = torch.randn(1, 1, 128, 64)
torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    input_names=["input"],
    output_names=["output"],
    opset_version=13
)

# 3. Convert ONNX to TensorFlow
onnx_model = onnx.load("model.onnx")
tf_rep = prepare(onnx_model)
tf_rep.export_graph("model_tf")

# 4. Convert TensorFlow SavedModel to TFLite
converter = tf.lite.TFLiteConverter.from_saved_model("model_tf")
tflite_model = converter.convert()

with open("model.tflite", "wb") as f:
    f.write(tflite_model)

print("✔ model.tflite generated successfully!")
