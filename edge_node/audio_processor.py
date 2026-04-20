import numpy as np
import torch
import random
import time

class AudioFeatureExtractor:
    \"\"\"
    Simulates extracting Mel-spectrogram features from an audio stream.
    For this hackathon POC, since real PII/audio isn't allowed to be sent to the cloud,
    this component guarantees extraction strictly locally and we simulate the inputs.
    \"\"\"
    def __init__(self, sample_rate=16000, n_mels=64, frame_length=64):
        self.sample_rate = sample_rate
        self.n_mels = n_mels
        self.frame_length = frame_length

    def simulate_audio_capture(self, force_anomaly=False):
        \"\"\"
        Simulates capturing 1 second of audio data and processing it.
        Creates a (1, 1, 64, 64) tensor for our CNN.
        \"\"\"
        # We simulate the \"feature\" space directly.
        # In a real scenario, we'd use librosa for raw wav -> mel spectrogram
        # Here, normal background noise will have random values around 0, 
        # Anomalies will have sharp peaks.
        
        feature_map = np.random.normal(loc=-1.0, scale=0.5, size=(1, 1, self.n_mels, self.frame_length))
        
        true_label = 0 # 0: Normal
        
        if force_anomaly:
            anomaly_type = random.choice([1, 2]) # 1: Gunshot, 2: Distress
            true_label = anomaly_type
            
            # Simulate a "loud peak" in the spectrogram
            start = random.randint(10, 50)
            length = random.randint(5, 10)
            feature_map[:, :, :, start:start+length] += 3.0 # Spike in volume/energy
            
        return torch.tensor(feature_map, dtype=torch.float32), true_label

if __name__ == "__main__":
    extractor = AudioFeatureExtractor()
    feat, label = extractor.simulate_audio_capture(force_anomaly=True)
    print(f"Captured feature shape: {feat.shape}, Label: {label}")
