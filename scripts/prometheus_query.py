import requests

PROMETHEUS_URL = "http://localhost:9090"

def query_prometheus(promql):
    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": promql}
    )
    data = response.json()
    print("Status:", data["status"])
    if data["status"] == "success":
        return data["data"]["result"]
    else:
        print("Error:", data)
        return []

# Requête CPU
cpu_data = query_prometheus('node_cpu_seconds_total')
print("=== CPU DATA ===")
for item in cpu_data[:3]:
    print(f"Value: {item['value'][1]}")

# Requête Mémoire
mem_data = query_prometheus('node_memory_MemAvailable_bytes')
print("\n=== MEMORY ===")
for item in mem_data:
    print(f"Memory: {float(item['value'][1]) / 1e9:.2f} GB available")
