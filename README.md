# Food Multi Agent Recommender System
This project explores how expert dietary knowledge can be systematically integrated into **multi-agent systems (MAS)** to generate **personalized ketogenic recipe recommendations**.  

Using the **MacRec framework**, we developed a two-stage architecture:
1. **Knowledge-based pre-filter** – narrows down recipes according to evidence-based ketogenic guidelines.
2. **Analyst & Reflector agents** – iteratively optimize recommendations to balance health goals and user preferences.

This modular design provides:
- **Transparency** – explicit control over the trade-off between health and user satisfaction.
- **Personalization** – tailoring recipes while promoting keto compliance.
- **Flexibility** – ability to adjust between strict adherence and broader recipe diversity.

Our experiments show that this approach improves both **dietary compliance** and **recommendation accuracy**. While strict configurations maximize adherence, they reduce diversity and increase runtime — highlighting the trade-offs between **validity, diversity, and efficiency**.

This repository provides the implementation and simulation code for experimenting with MAS-based, knowledge-driven dietary recommender systems.

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
