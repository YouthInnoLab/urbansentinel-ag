import flwr as fl

# Define strategy for federated aggregation
# We use FedAvg (Federated Averaging), the standard algorithm for FL.
strategy = fl.server.strategy.FedAvg(
    fraction_fit=1.0,  # Sample 100% of available clients for training
    fraction_evaluate=1.0,  # Sample 100% of available clients for evaluation
    min_fit_clients=2,  # Never start training without at least 2 clients
    min_evaluate_clients=2,  # Never start evaluation without at least 2 clients
    min_available_clients=2,  # Wait until at least 2 clients are connected
)

if __name__ == "__main__":
    print("Starting UrbanSentinel Federated Aggregation Server...")
    # Start Flower server
    fl.server.start_server(
        server_address="0.0.0.0:8080",
        config=fl.server.ServerConfig(num_rounds=3),
        strategy=strategy,
    )
