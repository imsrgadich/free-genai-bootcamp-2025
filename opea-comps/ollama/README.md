# Introduction
Ollama allows you to run open-source large language models, such as Llama 3, locally. Ollama bundles model weights, configuration, and data into a single package, defined by a Modelfile. Ollama is a lightweight, extensible framework for building and running language models on the local machine. It provides a simple API for creating, running, and managing models, as well as a library of pre-built models that can be easily used in a variety of applications. It's the best choice to deploy large language models on AIPC locally.

# Prerequisite
- Install docker by running the following.
```
curl -fsSL https://get.docker.com -o install_docker.sh
chmod +x ./install_docker.sh
./install_docker.sh
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

# Implementation steps
- Copy the docker-compose.yml file from the [repo](https://github.com/opea-project/GenAIComps/tree/main/comps/third_parties/ollama/deployment/docker_compose).

- Navigate to docker-compose.yml directory. 
```
cd opea-comps/ollama/deployments
LLM_ENDPOINT_PORT=8008 LLM_MODEL_ID="llama3.2:1b" host_ip=172.17.0.1 docker compose up
```

- Pull the model first in the Ollama server by running
```
curl -X POST http://localhost:8008/api/pull -d '{
  "model": "llama3.2:1b"
}'
```

- Run the following command to get response from the Ollama server
```
curl --noproxy "*" http://localhost:8008/api/generate -d '{
   "model": "llama3.2:1b",
   "prompt":"Why is the sky blue?"
 }'
```
