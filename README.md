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

# Deployment v2 -- Auto Scaling Group + Monitoring (Prometheus)

# Architecture

Browser → ALB (**Port 80**) → Target Group (**Port 8000**) → EC2
(Docker) → FastAPI (**Port 8000**)

Prometheus → EC2 Service Discovery → EC2 (**Port 8000**) for application
metrics → EC2 (**Port 9100**) for Node Exporter → EC2 (**Port 9121**)
for Redis Exporter

------------------------------------------------------------------------

# IMPORTANT PORTS (MEMORIZE)

  Component                   Port
  --------------------------- ---------------------
  ALB Listener                **80**
  Target Group Traffic Port   **8000**
  FastAPI                     **8000**
  FastAPI Metrics             **8000 (/metrics)**
  Node Exporter               **9100**
  Redis Exporter              **9121**
  Prometheus                  **9090**

> **Golden Rule:**\
> ALB listens on **80**.\
> Application listens on **8000**.\
> Target Group forwards to **8000**.\
> Prometheus scrapes the **EC2 directly**, not the ALB.

------------------------------------------------------------------------

# Step 1 -- Upload Deployment Files

Upload `docker-compose.yaml` and `.env` to S3.

------------------------------------------------------------------------

# Step 2 -- Launch Template

While creating the Launch Template:

-   AMI: Ubuntu
-   Instance Profile with:
    -   AmazonEC2ContainerRegistryReadOnly
    -   AmazonS3ReadOnlyAccess
-   Security Group
-   **Tag Name = `my-asg-instance`**

The **Name tag is critical** because Prometheus EC2 Service Discovery
filters instances using this tag.

User Data:

``` bash
#!/bin/bash
set -e

apt-get update -y
apt-get upgrade -y

apt-get install -y docker.io docker-compose-v2 unzip curl

systemctl enable docker
systemctl start docker

usermod -aG docker ubuntu

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"

cd /tmp
unzip -o awscliv2.zip
./aws/install

mkdir -p /home/ubuntu/app
cd /home/ubuntu/app

aws s3 cp s3://pulse-play-recommender-bucket/docker-compose.yaml .
aws s3 cp s3://pulse-play-recommender-bucket/.env .

aws ecr get-login-password --region eu-north-1 \
| docker login \
--username AWS \
--password-stdin 660838764267.dkr.ecr.eu-north-1.amazonaws.com

docker compose up -d

wget https://github.com/prometheus/node_exporter/releases/download/v1.10.2/node_exporter-1.10.2.linux-amd64.tar.gz
tar xvfz node_exporter-1.10.2.linux-amd64.tar.gz
cd node_exporter-1.10.2.linux-amd64
./node_exporter &
```

------------------------------------------------------------------------

# Step 3 -- Create Target Group

-   Protocol: HTTP
-   **Traffic Port = 8000**
-   Target Type = Instance

Health Check:

-   Protocol: HTTP
-   **Port = Traffic Port**
-   Path:

```{=html}
<!-- -->
```
    /internal/health

------------------------------------------------------------------------

# Step 4 -- Create Application Load Balancer

Listener:

**HTTP : 80**

Forward to Target Group.

Never expose FastAPI directly to the Internet.

Users should access:

    http://<ALB_DNS>/

NOT

    http://<ALB_DNS>:8000

------------------------------------------------------------------------

# Step 5 -- Create Auto Scaling Group

Select:

-   Launch Template
-   Target Group
-   ALB

Verify the instance is registered and Healthy.

------------------------------------------------------------------------

# Step 6 -- Monitoring EC2

Create another Ubuntu EC2.

Install:

-   Prometheus
-   Grafana
-   AWS CLI

Attach IAM Role:

-   AmazonEC2ReadOnlyAccess

This permission is required for EC2 Service Discovery.

------------------------------------------------------------------------

# Prometheus Configuration

Important scrape jobs:

``` yaml
scrape_configs:

- job_name: 'pulse-play'
  ec2_sd_configs:
    - region: eu-north-1
      port: 8000
  metrics_path: /metrics
  relabel_configs:
    - source_labels: [__meta_ec2_tag_Name]
      regex: .*my-asg-instance.*
      action: keep

- job_name: 'ec2-asg-instances'
  ec2_sd_configs:
    - region: eu-north-1
      port: 9100
  relabel_configs:
    - source_labels: [__meta_ec2_tag_Name]
      regex: .*my-asg-instance.*
      action: keep

- job_name: 'redis-exporter'
  ec2_sd_configs:
    - region: eu-north-1
      port: 9121
  relabel_configs:
    - source_labels: [__meta_ec2_tag_Name]
      regex: .*my-asg-instance.*
      action: keep
```

## Why EC2 Service Discovery?

Prometheus queries the AWS EC2 API to discover instances dynamically.

Whenever an ASG launches or terminates an instance:

-   No Prometheus configuration changes are required.
-   Targets are added and removed automatically.

------------------------------------------------------------------------

# Important Concepts

## Users

Browser

→ ALB (**80**)

→ Target Group (**8000**)

→ FastAPI (**8000**)

## Monitoring

Prometheus

→ EC2 (**8000**)

→ `/metrics`

Prometheus **does not scrape through the ALB**.

------------------------------------------------------------------------

# Common Mistakes

-   ALB Listener = 80
-   Target Group = 8000
-   FastAPI = 8000

Never configure:

-   Target Group = 80
-   FastAPI = 8000

This causes:

-   Healthy health checks (if configured differently)
-   502 Bad Gateway for users

Always ensure:

-   Target Group Traffic Port == FastAPI Port

------------------------------------------------------------------------

# Troubleshooting Checklist

-   `curl http://localhost:8000/internal/health`
-   `curl http://localhost:8000/metrics`
-   `docker ps`
-   `docker logs <container>`
-   `aws elbv2 describe-target-health`
-   `./promtool check config prometheus.yml`

If Prometheus shows **0 / 0 up**, check:

-   IAM Role
-   Name tag (`my-asg-instance`)
-   `ec2_sd_configs`
-   YAML indentation
-   Region
-   Service Discovery page

If Prometheus shows **DOWN**, check:

-   Node Exporter
-   Redis Exporter
-   FastAPI metrics endpoint
-   Security Groups
-   Port numbers
