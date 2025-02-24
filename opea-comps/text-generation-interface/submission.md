# Overview
- I used my local machine (NVIDIA GPU RTX 3090) and Github codespaces (2cores, 8GB RAM) to develop this. I used my Macbook M3 Pro with ssh to Windows machine on Cursor AI IDE.
- I started implementing while watching your video. 
- I had to create two docker-compose files, one for cpu specific and other for gpu one. I had issues with local deployment as CUDA was not setup.
- I had to pull the model first (which was not part of OPEA docs) and them call the service. 

# Tasks
1. Ollama Docker Microservice

Repo: https://github.com/imsrgadich/free-genai-bootcamp-2025/tree/main/opea-comps/ollama-microservice

It was quite straight forward to get this working. 

## Technical Implementation
### Prerequisite
- Install docker by running the following. In WSL, follow the Windows documentation. 
```
curl -fsSL https://get.docker.com -o install_docker.sh
chmod +x ./install_docker.sh
./install_docker.sh
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

### Implementation steps
- Copy the docker-compose.yml file from the [repo](https://github.com/opea-project/GenAIComps/tree/main/comps/third_parties/ollama/deployment/docker_compose).

- Navigate to docker-compose.yml directory and run docker compose based on your type of the machine.
```
# for cpu only machines
cd opea-comps/ollama/deployment
LLM_ENDPOINT_PORT=8008 LLM_MODEL_ID="llama3.2:1b" host_ip=$(hostname -I | awk '{print $1}') docker compose -f docker-compose-cpu.yml up
```

```
# for nvidia gpu machines
cd opea-comps/ollama/deployment
LLM_ENDPOINT_PORT=8008 LLM_MODEL_ID="llama3.2:1b" host_ip=$(hostname -I | awk '{print $1}') docker compose -f docker-compose-nvidia.yml up
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

2. Text Generation Interface

Repo: https://github.com/imsrgadich/free-genai-bootcamp-2025/tree/main/opea-comps/text-generation-interface

- I had issues with importing opea comps/cores and comps/llms/src/text-generation with related modules. Pip install didn't work, so I had to manually copy the files from GenAI comps repo and add it here. I created a __init__.py file to be able to import it properly. 
- I followed the instructions to on how to use the Ollama server in the step 1 by assigning necessary environment variables. 
- I successfully managed to run the Text Generation Service. 


# Technical Implementation
## Prerequisite
- Install docker by running the following. In WSL, follow the Windows documentation. 
```
curl -fsSL https://get.docker.com -o install_docker.sh
chmod +x ./install_docker.sh
./install_docker.sh
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

## Implementation steps
- Create the conda virtual environment and activate it.
```
conda create -n text-generation-interface python=3.12 
conda activate text-generation-interface
```
- Install the dependencies
```
cd opea-comps
pip install -r text-generation-interface/requirements.yml
```
- Prepare the docker image.
 ```
 # Build the microservice docker
cd opea-comps

docker build \
  --build-arg https_proxy=$https_proxy \
  --build-arg http_proxy=$http_proxy \
  -t opea/llm-textgen:latest \
  -f text-generation-interface/Dockerfile .
 ```
 - To start the docker service 

 1. Export the environment variables
 ```
export LLM_ENDPOINT_PORT=8008
export TEXTGEN_PORT=9000
export host_ip=$(hostname -I | awk '{print $1}')
export HF_TOKEN=${HF_TOKEN} 
export LLM_ENDPOINT="http://${host_ip}:${LLM_ENDPOINT_PORT}"
export LLM_MODEL_ID="llama3.2:1b"
export LLM_COMPONENT_NAME="OpeaTextGenService"
 ```
 2. Run the microservice
 ```
# Stop the existing container
docker stop llm-textgen-server

# Remove the existing container
docker rm llm-textgen-server

# Run the microservice
docker run \
  --name="llm-textgen-server" \
  -p $TEXTGEN_PORT:9000 \
  --ipc=host \
  -e http_proxy=$http_proxy \
  -e https_proxy=$https_proxy \
  -e no_proxy=${no_proxy} \
  -e LLM_ENDPOINT=$LLM_ENDPOINT \
  -e HF_TOKEN=$HF_TOKEN \
  -e LLM_MODEL_ID=$LLM_MODEL_ID \
  -e LLM_COMPONENT_NAME=$LLM_COMPONENT_NAME \
  opea/llm-textgen:latest
 ```

 3. Consume the service. If necessary export the environment variables again, if running in different bash.
 ```
 curl http://${host_ip}:${TEXTGEN_PORT}/v1/health_check\
  -X GET \
  -H 'Content-Type: application/json'
 ```

To verify the microservice:

You can set the following model parameters according to your actual needs, such as max_tokens, stream.

The stream parameter determines the format of the data returned by the API. It will return text string with stream=false, return text stream flow with stream=true.

 ```
 # stream mode
curl http://${host_ip}:${TEXTGEN_PORT}/v1/chat/completions \
    -X POST \
    -d '{"model": "${LLM_MODEL_ID}", "messages": "What is Deep Learning?", "max_tokens":17}' \
    -H 'Content-Type: application/json'

curl http://${host_ip}:${TEXTGEN_PORT}/v1/chat/completions \
    -X POST \
    -d '{"model": "${LLM_MODEL_ID}", "messages": [{"role": "user", "content": "What is Deep Learning?"}], "max_tokens":17}' \
    -H 'Content-Type: application/json'

#Non-stream mode
curl http://${host_ip}:${TEXTGEN_PORT}/v1/chat/completions \
    -X POST \
    -d '{"model": "${LLM_MODEL_ID}", "messages": "What is Deep Learning?", "max_tokens":17, "stream":false}' \
    -H 'Content-Type: application/json'
 ```