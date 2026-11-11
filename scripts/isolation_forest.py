import requests
import numpy as np
from sklearn.ensemble import IsolationForest
import time
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

PROMETHEUS_URL = "http://localhost:9090"

def get_cpu():
    r = requests.get(f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": "sum(rate(container_cpu_usage_seconds_total{pod=~'web-app.*'}[1m]))"})
    results = r.json()["data"]["result"]
    return float(results[0]["value"][1]) if results else 0.0

def get_memory():
    r = requests.get(f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": "sum(container_memory_usage_bytes{pod=~'web-app.*'})"})
    results = r.json()["data"]["result"]
    return float(results[0]["value"][1]) / 1e6 if results else 0.0

def get_restarts():
    r = requests.get(f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": "sum(kube_pod_container_status_restarts_total{pod=~'web-app.*'})"})
    results = r.json()["data"]["result"]
    return float(results[0]["value"][1]) if results else 0.0

# ÉTAPE 1 — Collecter données normales
print("Collecte des données normales (20 lectures)...")
X_train = []
for i in range(20):
    cpu = get_cpu()
    mem = get_memory()
    restarts = get_restarts()
    X_train.append([cpu, mem, restarts])
    print(f"Lecture {i+1}/20 → CPU: {cpu:.4f} | Mem: {mem:.2f}MB | Restarts: {restarts}")
    time.sleep(2)

# ÉTAPE 2 — Entraîner le modèle
print("\nEntraînement du modèle Isolation Forest...")
model = IsolationForest(contamination=0.05, random_state=42)
model.fit(X_train)
print("Modèle entraîné! ✅")

# Préparer la métrique Prometheus (Pushgateway)
registry = CollectorRegistry()
anomaly_score_gauge = Gauge('anomaly_score', 'Isolation Forest anomaly score', registry=registry)

# ÉTAPE 3 — Surveillance
print("\nSurveillance en cours...")
while True:
    cpu = get_cpu()
    mem = get_memory()
    restarts = get_restarts()
    x = [[cpu, mem, restarts]]
    label = model.predict(x)
    score = model.decision_function(x)[0]

    # Envoi du score vers Pushgateway → Prometheus → Grafana
    anomaly_score_gauge.set(score)
    push_to_gateway('localhost:9091', job='isolation_forest', registry=registry)

    if label[0] == -1:
        print(f"⚠️  ANOMALIE! CPU:{cpu:.4f} Mem:{mem:.2f}MB Restarts:{restarts} Score:{score:.4f}")
    else:
        print(f"✅ Normal — CPU:{cpu:.4f} Mem:{mem:.2f}MB Restarts:{restarts} Score:{score:.4f}")
    time.sleep(3)
