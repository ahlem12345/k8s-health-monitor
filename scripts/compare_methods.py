import requests
import numpy as np
from sklearn.ensemble import IsolationForest
import time
import csv
from datetime import datetime

PROMETHEUS_URL = "http://localhost:9090"
CSV_FILE = "anomalies_log.csv"

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

# Préparer le fichier CSV
with open(CSV_FILE, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "cpu", "memory_mb", "restarts", "method", "anomaly"])

# ÉTAPE 1 — Collecter données normales (pour les 2 méthodes)
print("Collecte des données normales (20 lectures)...")
cpu_history = []
X_train = []
for i in range(20):
    cpu = get_cpu()
    mem = get_memory()
    restarts = get_restarts()
    cpu_history.append(cpu)
    X_train.append([cpu, mem, restarts])
    print(f"Lecture {i+1}/20 → CPU: {cpu:.4f} | Mem: {mem:.2f}MB | Restarts: {restarts}")
    time.sleep(2)

# Méthode 1 — Calcul du seuil statistique
mean = np.mean(cpu_history)
std = np.std(cpu_history)
threshold = mean + 2 * std
print(f"\n[Statistique] Seuil d'anomalie CPU: {threshold:.4f}")

# Méthode 2 — Entraîner Isolation Forest
model = IsolationForest(contamination=0.05, random_state=42)
model.fit(X_train)
print("[Isolation Forest] Modèle entraîné ✅")

# ÉTAPE 2 — Surveillance avec les 2 méthodes en parallèle
print("\nSurveillance en cours (2 méthodes en parallèle)...\n")
count_stat = 0
count_iso = 0
total = 0

while True:
    cpu = get_cpu()
    mem = get_memory()
    restarts = get_restarts()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total += 1

    # Méthode statistique
    stat_anomaly = cpu > threshold

    # Méthode Isolation Forest
    x = [[cpu, mem, restarts]]
    iso_label = model.predict(x)[0]
    iso_anomaly = iso_label == -1

    # Affichage comparatif
    print(f"[{timestamp}] CPU:{cpu:.4f} Mem:{mem:.2f}MB Restarts:{restarts} "
          f"| Statistique: {'⚠️ ANOMALIE' if stat_anomaly else '✅ Normal'} "
          f"| Isolation Forest: {'⚠️ ANOMALIE' if iso_anomaly else '✅ Normal'}")

    # Log dans le CSV si anomalie détectée par au moins une méthode
    if stat_anomaly:
        count_stat += 1
        with open(CSV_FILE, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, cpu, mem, restarts, "Statistique", "OUI"])

    if iso_anomaly:
        count_iso += 1
        with open(CSV_FILE, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, cpu, mem, restarts, "IsolationForest", "OUI"])

    time.sleep(3)
