This Repository will help Avanindra to learn about Observability.
# Deployment Steps on EC2 with Monitoring setup:

# Pulse Play Hybrid Recommender System

# Deployment Guide (EC2)

> **Scope**
>
> This guide demonstrates deployment of Pulse Play on **two standalone EC2 instances only**.
>
> It **does NOT** use:
>
> - ECS
> - EKS
> - Auto Scaling Groups
> - Load Balancers
> - ElastiCache
> - RDS
>
> This deployment is intended for learning Docker, Prometheus, Grafana, and EC2.

---

# Architecture

```
                    Internet
                         │
                         │
                 http://APP_EC2:8000
                         │
        ┌────────────────────────────────┐
        │       Application EC2          │
        │--------------------------------│
        │ FastAPI (Docker)               │
        │ Redis (Docker)                 │
        │ Redis Exporter (Docker)        │
        └────────────────────────────────┘
                         │
                  Prometheus Scrapes
                         │
        ┌────────────────────────────────┐
        │       Monitoring EC2           │
        │--------------------------------│
        │ Prometheus                     │
        │ Grafana                        │
        │ Node Exporter                  │
        └────────────────────────────────┘
```

---

# EC2 Instance 1 (Application Server)

---

## 1. Update Ubuntu

```bash
sudo apt update
sudo apt upgrade -y
```

---

## 2. Install Docker

```bash
sudo apt install docker.io -y

sudo systemctl enable docker

sudo systemctl start docker
```

Verify

```bash
docker --version
```

---

## 3. Allow Docker Without sudo

```bash
sudo usermod -aG docker $USER

newgrp docker
```

Verify

```bash
docker ps
```

---

## 4. Install Docker Compose

```bash
sudo apt install docker-compose-v2 -y
```

Verify

```bash
docker compose version
```

---

## 5. Install AWS CLI

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

sudo apt install unzip -y

unzip awscliv2.zip

sudo ./aws/install
```

Verify

```bash
aws --version
```

---

## 6. Configure AWS CLI

```bash
aws configure
```

Provide

- Access Key
- Secret Key
- Region
- Output = json

Verify

```bash
aws s3 ls
```

---

## 7. Download Deployment Files

```bash
aws s3 cp s3://<bucket-name>/docker-compose.yaml .
```

---

## 8. Create Environment Variables

```bash
nano .env
```

Paste all environment variables.

Save

```
CTRL + O

ENTER

CTRL + X
```

Verify

```bash
cat .env
```

---

## 9. Login to Amazon ECR

```bash
aws ecr get-login-password --region <region> \
| docker login \
--username AWS \
--password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
```

---

## 10. Pull Docker Image

```bash
docker pull <account-id>.dkr.ecr.<region>.amazonaws.com/pulse-play-hybrid-recommender:latest
```

---

## 11. Start Containers

```bash
docker compose up -d
```

Verify

```bash
docker ps
```

Expected containers

- FastAPI
- Redis
- Redis Exporter

---

## 12. Troubleshooting (Exit Code 137)

If FastAPI exits with

```
Exited (137)
```

The application has run out of memory.

Check memory

```bash
free -h
```

Create a 2GB swap file

```bash
sudo fallocate -l 2G /swapfile

sudo chmod 600 /swapfile

sudo mkswap /swapfile

sudo swapon /swapfile
```

Verify

```bash
free -h
```

Persist swap after reboot

```bash
sudo nano /etc/fstab
```

Append

```
/swapfile none swap sw 0 0
```

---

## 13. Verify Application

```bash
curl http://localhost:8000
```

Browser

```
http://<Application-Public-IP>:8000
```

---

# Application Security Group

Allow

| Port | Purpose |
|------|----------|
|22|SSH|
|8000|FastAPI|
|9121|Redis Exporter|

---

# EC2 Instance 2 (Monitoring)

---

## 1. Update Ubuntu

```bash
sudo apt update
sudo apt upgrade -y
```

---

# Install Prometheus

```bash
wget https://github.com/prometheus/prometheus/releases/download/v3.4.2/prometheus-3.4.2.linux-amd64.tar.gz

tar xvf prometheus-3.4.2.linux-amd64.tar.gz

cd prometheus-3.4.2.linux-amd64
```

---

## Configure Prometheus

```bash
nano prometheus.yml
```

Example

```yaml
scrape_configs:

  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: "Pulse_Play"
    static_configs:
      - targets:
          - "<APPLICATION_PUBLIC_IP>:8000"

  - job_name: "Redis_Exporter"
    static_configs:
      - targets:
          - "<APPLICATION_PUBLIC_IP>:9121"

  - job_name: "Node_Exporter"
    static_configs:
      - targets:
          - "<MONITORING_PUBLIC_IP>:9100"
```

---

## Start Prometheus

```bash
./prometheus --config.file=prometheus.yml &
```

Verify

```bash
ps -ef | grep prometheus
```

---

# Install Grafana

```bash
sudo apt-get install -y apt-transport-https software-properties-common wget

sudo mkdir -p /etc/apt/keyrings/

wget -q -O - https://apt.grafana.com/gpg.key \
| gpg --dearmor \
| sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null

echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" \
| sudo tee -a /etc/apt/sources.list.d/grafana.list

sudo apt-get update

sudo apt-get install grafana-enterprise

sudo systemctl start grafana-server

sudo systemctl enable grafana-server
```

Access

```
http://<MONITORING_PUBLIC_IP>:3000
```

Default credentials

```
admin
admin
```

---

# Install Node Exporter

Download

```bash
wget https://github.com/prometheus/node_exporter/releases/download/v1.10.2/node_exporter-1.10.2.linux-amd64.tar.gz
```

Extract

```bash
tar xvfz node_exporter-1.10.2.linux-amd64.tar.gz
```

Navigate

```bash
cd node_exporter-1.10.2.linux-amd64
```

Run

```bash
./node_exporter
```

Run in background

```bash
nohup ./node_exporter > node_exporter.log 2>&1 &
```

Verify

```bash
curl http://localhost:9100/metrics
```

---

# Monitoring Security Group

Allow

| Port | Purpose |
|------|----------|
|22|SSH|
|3000|Grafana|
|9090|Prometheus|
|9100|Node Exporter|

---

# Useful Debugging Commands

Docker

```bash
docker ps

docker ps -a

docker logs fast-api

docker logs -f fast-api

docker stats
```

Memory

```bash
free -h

df -h
```

AWS CLI

```bash
aws s3 ls

aws s3 cp <source> <destination>
```

Prometheus

```bash
ps -ef | grep prometheus

curl http://localhost:9090
```

Grafana

```bash
sudo systemctl status grafana-server
```

Node Exporter

```bash
curl http://localhost:9100/metrics
```

---

# Final Notes

This deployment guide is intended **only for a single EC2-based learning environment**. It demonstrates how to deploy a containerized FastAPI application with Redis, expose metrics to Prometheus, visualize them in Grafana, and monitor EC2 hardware metrics using Node Exporter. It deliberately avoids production services such as ECS, EKS, Auto Scaling Groups, Load Balancers, ElastiCache, and managed databases.
