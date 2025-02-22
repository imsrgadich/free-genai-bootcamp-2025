# Stage 1: Build Python dependencies
FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.11 AS builder

# Set working directory and ownership
WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Stage 2: Runtime with AWS Lambda
FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.11

# Install Ollama and its dependencies
RUN yum update -y \
    && yum install -y curl \
    && curl -L https://ollama.ai/download/ollama-linux-amd64 -o /usr/local/bin/ollama \
    && chmod +x /usr/local/bin/ollama \
    && rm -rf /var/cache/yum

# Set up Ollama environment
ENV HOME=/tmp
ENV OLLAMA_MODELS=/tmp/.ollama/models

# Copy Python dependencies and function code
COPY --from=builder ${LAMBDA_TASK_ROOT} ${LAMBDA_TASK_ROOT}
COPY lambda_function.py ${LAMBDA_TASK_ROOT}
COPY entrypoint.sh ${LAMBDA_TASK_ROOT}

RUN chmod +x ${LAMBDA_TASK_ROOT}/entrypoint.sh

# Set the handler
CMD ["lambda_function.lambda_handler"]
