#!/bin/bash

echo "Stoppe Elasticsearch-Container (falls aktiv)..."
sudo docker stop elasticsearch_container 2>/dev/null || echo "Container lief nicht."
