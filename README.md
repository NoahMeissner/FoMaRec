# Food Multi Agent Recommender System
# Project Setup & Usage

This repository contains code that runs on **Elasticsearch 8.17.4** inside Docker and provides two main entry points:  
- `main.py` – for initializing or running the core service  
- `run_simulation.py` – for running simulations  

Follow the steps below to set up and run everything locally.

---

## 🐳 1. Install & Run Elasticsearch in Docker (v8.17.4)

Make sure you have [Docker](https://docs.docker.com/get-docker/) installed.

Run the following command to start Elasticsearch 8.17.4 in a container:

```bash
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  docker.elastic.co/elasticsearch/elasticsearch:8.17.4

## Check if Elastic is running
curl http://localhost:9200

## Install Python Dependencies
```bash
python3 -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)
pip install -r requirements.txt
```
## Edit .env
Edit your Api Keys

## Download Dataset
Save it in the Config/dataset Folder

## Run main.py (create embeddings)
```bash
python main.py
```

## Run simulation
```bash
python run_simulation.py
```
