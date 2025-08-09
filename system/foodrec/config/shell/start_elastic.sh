#!/bin/bash

echo "Starte Docker-Daemon (falls nicht bereits gestartet)..."
sudo systemctl start docker

echo "Starte Elasticsearch-Container..."
sudo docker run --rm \
  --name elasticsearch_container \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.17.4
