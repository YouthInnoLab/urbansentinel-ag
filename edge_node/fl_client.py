import os
import flwr as fl
import torch
import torch.nn as nn
from collections import OrderedDict
from model import AcousticAnomalyModel

# Device configuration
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

class UrbanSentinelClient(fl.client.NumPyClient):
    def __init__(self, model):
        self.model = model

    def get_parameters(self, config):
        return [val.cpu().numpy() for _, val in self.model.state_dict().items()]

    def set_parameters(self, parameters):
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        self.model.load_state_dict(state_dict, strict=True)

    def fit(self, parameters, config):
        self.set_parameters(parameters)
        
        # In a real scenario, the edge node would have collected a local dataset of
        # pseudo-labeled anomalies or ambient background noise over the week.
        # We simulate a tiny training epoch here.
        print(f"\\n--- Node performing Local Federated Retraining ---")
        self.model.train()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        criterion = nn.CrossEntropyLoss()
        
        # Mocking 1 batch of local data (e.g. ambient noise)
        mock_data = torch.randn(8, 1, 64, 64).to(DEVICE)
        mock_target = torch.zeros(8, dtype=torch.long).to(DEVICE) # Label 0: Background
        
        optimizer.zero_grad()
        output = self.model(mock_data)
        loss = criterion(output, mock_target)
        loss.backward()
        optimizer.step()
        
        print("Local weights updated. Sending diff to aggregation server without raw data.")
        
        # Return updated parameters, dataset size, and metrics
        return self.get_parameters(config={}), 8, {}

    def evaluate(self, parameters, config):
        self.set_parameters(parameters)
        # Mock evaluation loss and accuracy
        return float(1.0), 8, {"accuracy": 0.95}

if __name__ == "__main__":
    print("Starting Edge Node FL Client...")
    model = AcousticAnomalyModel().to(DEVICE)
    client = UrbanSentinelClient(model)
    fl.client.start_client(server_address="127.0.0.1:8080", client=client.to_client())
