import time
import json
import torch
import torch.nn.functional as F
import asyncio
import websockets
import random
import uuid
import datetime
from model import AcousticAnomalyModel
from audio_processor import AudioFeatureExtractor

NODE_ID = str(uuid.uuid4())[:8]
# Simulate a random location in a city (e.g., New York coordinates roughly)
LAT = 40.7128 + random.uniform(-0.05, 0.05)
LON = -74.0060 + random.uniform(-0.05, 0.05)

WS_URL = "ws://localhost:8000/ws/edge"

class InferenceEngine:
    def __init__(self):
        self.model = AcousticAnomalyModel()
        self.model.eval()
        self.extractor = AudioFeatureExtractor()
        # Initialize with random weights
        
    async def send_alert(self, class_val, confidence):
        alert_type = "Gunshot" if class_val == 1 else "Distress/Fall"
        payload = {
            "node_id": NODE_ID,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "lat": LAT,
            "lon": LON,
            "alert_type": alert_type,
            "confidence": round(float(confidence), 2)
        }
        print(f"[{NODE_ID}] ALARM TRIGGERED! {alert_type} detected (Conf: {confidence:.2f}). Dispatching...")
        try:
            async with websockets.connect(WS_URL) as websocket:
                await websocket.send(json.dumps(payload))
                print(f"[{NODE_ID}] Alert successfully sent to command center.")
        except Exception as e:
            print(f"[{NODE_ID}] Failed to connect to server: {e}")

    async def run(self):
        print(f"Starting UrbanSentinel Edge Node [{NODE_ID}]")
        print(f"Location: {LAT:.4f}, {LON:.4f}")
        
        while True:
            # 1. Capture streaming data securely on-device
            # We randomly inject anomalies 5% of the time to simulate a rare event
            force_anomaly = random.random() < 0.05 
            features, true_label = self.extractor.simulate_audio_capture(force_anomaly=force_anomaly)
            
            # 2. Run local Anomaly Detection 
            # (Raw data never leaves this scope)
            with torch.no_grad():
                logits = self.model(features)
                probs = F.softmax(logits, dim=1)
                confidence, pred_class = torch.max(probs, dim=1)
                
            pred_class_val = pred_class.item()
            conf_val = confidence.item()

            if pred_class_val != 0 and conf_val > 0.6:
                await self.send_alert(pred_class_val, conf_val)
            else:
                # Normal noise
                print(f"[{NODE_ID}] All clear. Local monitoring active...")
                
            # Simulate a 2-second capture window
            await asyncio.sleep(2)

if __name__ == "__main__":
    engine = InferenceEngine()
    asyncio.run(engine.run())
