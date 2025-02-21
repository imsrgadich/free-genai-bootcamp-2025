# LLM text generation Microservice
This microservice, designed for Language Model Inference (LLM), processes input consisting of a query string and associated reranked documents. It constructs a prompt based on the query and documents, which is then used to perform inference with a large language model. The service delivers the inference results as output.

A prerequisite for using this microservice is that users must have a LLM text generation service (etc., TGI, vLLM) already running. Users need to set the LLM service's endpoint into an environment variable. The microservice utilizes this endpoint to create an LLM object, enabling it to communicate with the LLM service for executing language model operations.

Overall, this microservice offers a streamlined way to integrate large language model inference into applications, requiring minimal setup from the user beyond initiating a TGI/vLLM service and configuring the necessary environment variables. This allows for the seamless processing of queries and documents to generate intelligent, context-aware responses.

## Implementation
- Create the conda virtual environment and activate it.
```
conda create -n text-generation-interface python=3.12 
conda activate text-generation-interface
```
- Install the dependencies
```
pip install -r requirements.yml
```
- Prepare the TGI docker image.
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
