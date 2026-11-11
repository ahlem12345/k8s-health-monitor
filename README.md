# Kubernetes Cluster Health Monitor with Anomaly Detection & Cybersecurity Monitoring

Projet de stage d'été: supervision d'un cluster Kubernetes local,
détection automatique d'anomalies en Python et surveillance de sécurité.

## Architecture
Windows 11 -> VirtualBox -> Ubuntu 22.04 -> Docker -> Minikube -> application Nginx (3 réplicas)
supervisée par Prometheus + Grafana, analysée par Python, sécurisée avec Trivy et Falco.

## Contenu
| Dossier | Description |
|---|---|
| `k8s/` | Déploiement Nginx sécurisé (securityContext, limites de ressources), Service et ServiceMonitor pour Falco et Pushgateway |
| `scripts/` | `prometheus_query.py` (requêtes API), `anomaly_statistical.py` (règle 2-sigma), `isolation_forest.py` (Isolation Forest), `compare_methods.py` (comparaison + journal CSV) |
| `results/` | `anomalies_log.csv` (anomalies détectées), `trivy_scan_result.txt` (scan de l'image nginx) |
| `screenshots/` | Captures : Grafana, détection d'anomalies, Trivy, Falco |
| `rapport/` | Rapport de stage (LaTeX et PDF) |

## Technologies
Kubernetes (Minikube), Helm, Prometheus, Grafana, Pushgateway, Python (requests, numpy,
scikit-learn, prometheus_client), Trivy, Falco.

## Étapes du projet
1. **Cluster et application** : Minikube, Deployment Nginx (3 pods), Service NodePort.
2. **Supervision** : kube-prometheus-stack (Helm), requêtes PromQL, tableau de bord Grafana.
3. **Détection d'anomalies** : règle 2-sigma vs Isolation Forest (CPU, mémoire, redémarrages), journal CSV.
4. **Sécurité** : securityContext (non-root, système de fichiers en lecture seule), scan Trivy
   (340 vulnérabilités sur nginx), détection d'intrusion Falco affichée dans Grafana.

## Lancer les scripts
Prérequis : Prometheus accessible sur `localhost:9090`
(`kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090`).
```bash
pip install requests numpy scikit-learn prometheus_client
python3 scripts/anomaly_statistical.py
python3 scripts/isolation_forest.py
python3 scripts/compare_methods.py
```

## Auteure
Ahlem Ben Salem 
