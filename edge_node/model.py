import torch
import torch.nn as nn
import torch.nn.functional as F

class AcousticAnomalyModel(nn.Module):
    \"\"\"
    A lightweight CNN for Audio Classification.
    Expected input shape: (Batch Size, Channels, Height, Width)
    Example: (1, 1, 64, 64) for Mel-Spectrogram features
    \"\"\"
    def __init__(self, num_classes=3):
        super(AcousticAnomalyModel, self).__init__()
        # Classes: 0: Normal City Noise, 1: Gunshot, 2: Distress/Scream/Fall
        
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        
        # After two MaxPool2d layers (for 64x64 input):
        # 64 -> 32 -> 16
        # Output size: 32 channels * 16 * 16
        self.fc1 = nn.Linear(32 * 16 * 16, 64)
        self.fc2 = nn.Linear(64, num_classes)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 32 * 16 * 16)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

if __name__ == "__main__":
    # Test model
    model = AcousticAnomalyModel()
    mock_input = torch.randn(1, 1, 64, 64)
    out = model(mock_input)
    print("Model Output Shape:", out.shape)
