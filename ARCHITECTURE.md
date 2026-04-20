# UrbanSentinel: Architecture & Implementation Document

## 1. Executive Summary
**UrbanSentinel** is a decentralized, privacy-preserving safety net designed to detect urban emergencies such as gunshots, falls, and medical distress. Unlike traditional cloud-based acoustic monitoring systems, UrbanSentinel relies entirely on **Edge AI** and **Federated Learning**. The system processes all acoustic data locally on edge devices (zero cloud storage of PII) and transmits only critical metadata anomalies and encrypted model weight updates, ensuring complete citizen privacy while maximizing dispatch efficiency.

---

## 2. System Architecture

The architecture is divided into three distinct geographic and logical layers: the Edge Layer, the Aggregation Layer, and the Presentation Layer.

### 2.1 The Edge Layer (On-Device Processing)
Each real-world unit (e.g., smart streetlamp, localized node) acts as an independent actor.
- **Acoustic Processor:** Continuously captures an audio stream in a rolling 2-second buffer. It actively extracts Mel-spectrogram features (mathematical representations of sound). **Action:** The raw audio is immediately truncated and never leaves this subsystem.
- **Anomaly Detection CNN:** A lightweight PyTorch Convolutional Neural Network (CNN) specifically tailored for multi-class audio classification. The model ingests the Mel-spectrograms and derives an acoustic classification.
- **Real-Time Dispatch Engine:** When an event is categorized as an anomaly (e.g., Gunshot, Distressed Voice/Fall) with a threshold confidence (e.g., > 60%), it encrypts a metadata payload (Node ID, Geolocation, Timestamp, Anomaly Type).
- **Federated Client:** Periodically executes brief, isolated training loops locally based on accumulated anomaly/false-positive pseudo-labels. It transmits strictly gradient matrices (weight updates) upstream.

### 2.2 The Aggregation Layer (Federated Learning Server)
Centralized but strictly sandboxed from actual civic data.
- **Federated Orchestrator:** Implemented via the `Flower` (flwr) framework. It initializes a global model state and signals available edge nodes for training rounds.
- **Weight Aggregation (`FedAvg`):** Receives model weight deltas from disparate edge nodes. Computes the geometric mean of the weights to enhance global accuracy (learning from different neighborhoods) and distributes the improved base model back to all nodes without ever centralizing their collected data.

### 2.3 The Presentation Layer (Command Center Broker & Dashboard)
- **FastAPI Broker:** The connective tissue tracking a massive influx of lightweight network endpoints. Operates a bidirectional WebSocket server that handles immediate upstream distress alerts and fans them out to connected Dashboards.
- **Dynamic Vite-React Dashboard:** Provides the geographic layout used by emergency dispatch. Features a premium glassmorphism overlay integrated over Carto Dark tiles with Leaflet, highlighting precise node locations dynamically whenever anomalies fire.

---

## 3. Implementation Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Edge AI Models** | Python, `torch`, `torchaudio` | Native, lightweight convolution computation |
| **Federated Learning** | `flwr` (Flower) | Low-overhead, robust FL aggregation pipeline |
| **Message Broker** | FastAPI, `websockets`, Uvicorn | Ultra-fast asyncio web streaming without MQTT overhead |
| **Front-End Application** | Vite, React, `react-leaflet`, Tailwind CSS | High-performance dynamic rendering and premium dark UI |

---

## 4. Test Plan & Validation Strategy

Our testing strategy demonstrates system resilience, zero-latency capabilities, and data-privacy assurances suitable for a Hackathon proof of concept.

### Phase 1: Edge Inference Verification
- **Objective:** Verify acoustic feature extraction correctly identifies distinct features without saving WAV files.
- **Action:** Run `edge_node/inference_engine.py` in isolated debug mode.
- **Success Criteria:** Console logs confirm periodic background scans. When random simulation parameters force a \"Gunshot\" signature into the Mel-spectrogram array, the PyTorch model correctly derives a Class #1 prediction with >60% confidence instantly. No audio files are produced or stored in the directory.

### Phase 2: Broker & Throughput Testing
- **Objective:** Ensure the FastAPI WebSocket broker correctly handles inbound alert events and routes them.
- **Action:** 
  1. Boot `backend/main.py`.
  2. Launch 3 separate instances of `inference_engine.py` simulating 3 separate streetlamps.
- **Success Criteria:** The broker prints successful connections for all 3 nodes. When any one node fires an alert, the JSON packet is correctly displayed in the router logs without dropped connections or throttling.

### Phase 3: Federated Learning Cycle Test
- **Objective:** Verify that local nodes can pull, train locally, and push weights securely without transmitting the pseudo-class datasets.
- **Action:** Boot `federated_server/server.py`. Start 2 instances of `fl_client.py` on distinct simulated terminals.
- **Success Criteria:** The server initiates a \"Federated Round\". Both nodes report back via logs that locally generated gradients were successfully packaged and transmitted. The server successfully performs `FedAvg` and distributes an updated model without errors.

### Phase 4: Full End-to-End System Integration (The Live Demo)
- **Objective:** Visually validate the real-time alerting pipeline under interactive user load.
- **Action:** 
  1. Initialize the FastAPI Broker server.
  2. Start the Vite React Dashboard (`npm run dev`) and open the browser.
  3. Start a few Edge Inference node simulators (`python inference_engine.py`).
- **Success Criteria:** 
  - The Web Dashboard successfully connects to the WebSocket stream (status icon goes green/\"Active\").
  - As nodes organically simulate gunshots or falls, glowing red/orange circle markers instantaneously \"pulse\" onto the geographic map at the designated NYC coordinates.
  - The UI accurately renders the confidence score and anomaly type alongside the precise Node ID.

## 5. Security & Privacy Addendum 
- The Edge Model operates entirely within the isolated memory scope on-device.
- At no point during Phase 1-4 tests is local microphone access routed over the WebSockets; only metadata (JSON) crosses the network.

---
*Generated for UrbanSentinel Hackathon 2026*
