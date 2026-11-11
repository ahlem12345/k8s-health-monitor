import requests
import numpy as np
import time

PROMETHEUS_URL = "http://localhost:9090"

def get_cpu():
    r = requests.get(f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": "rate(node_cpu_seconds_total{mode='user'}[1m])"})
    results = r.json()["data"]["result"]
    if results:
        return float(results[0]["value"][1])
    return 0.0

# Collecter 20 lectures normales
print("Collecte des données normales (20 lectures)...")
history = []
for i in range(20):
    cpu = get_cpu()
    history.append(cpu)
    print(f"Lecture {i+1}/20 → CPU: {cpu:.4f}")
    time.sleep(2)

# Appliquer la règle 2-sigma
mean = np.mean(history)
std = np.std(history)
threshold = mean + 2 * std

print(f"\nMoyenne: {mean:.4f}")
print(f"Écart-type: {std:.4f}")
print(f"Seuil d'anomalie: {threshold:.4f}")

# Tester une nouvelle lecture
print("\nSurveillance en cours...")
while True:
    cpu = get_cpu()
    if cpu > threshold:
        print(f"ANOMALIE DÉTECTÉE! CPU: {cpu:.4f} > Seuil: {threshold:.4f}")
    else:
        print(f" Normal — CPU: {cpu:.4f}")
    time.sleep(3)
