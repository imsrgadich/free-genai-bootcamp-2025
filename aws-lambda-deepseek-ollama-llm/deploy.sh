#!/bin/bash

# Exit on any error
set -e

# Function to handle errors
error_handler() {
    local line_number=$1
    local error_code=$2
    echo "Error occurred in script at line: ${line_number}, with exit code: ${error_code}"
    exit "${error_code}"
}

# Set up error handling
trap 'error_handler ${LINENO} $?' ERR

# Variables
AWS_REGION="eu-north-1"  # Change to your AWS region
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_NAME="ollama-llm-lambda"
IMAGE_TAG=$(date +%s)  # Unique timestamp for tagging
IMAGE_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:${IMAGE_TAG}"
STACK_NAME="OllamaLambdaStack"

echo "Starting deployment process..."

# Check if stack exists and delete if present
STACK_STATUS=$(aws cloudformation describe-stacks --stack-name ${STACK_NAME} --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "STACK_NOT_FOUND")

if [ "$STACK_STATUS" != "STACK_NOT_FOUND" ]; then
    echo "Existing stack found. Deleting stack..."
    aws cloudformation delete-stack --stack-name ${STACK_NAME}
    echo "Waiting for stack deletion to complete..."
    aws cloudformation wait stack-delete-complete --stack-name ${STACK_NAME}
    echo "Stack deleted successfully"
fi

# Step 1: Authenticate with AWS ECR - Using safer password handling
echo "Step 1: Logging in to Amazon ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com || {
    echo "Failed to authenticate with ECR"
    exit 1
}

# Step 2: Ensure ECR Repository Exists
echo "Step 2: Checking if ECR repository exists..."
if ! aws ecr describe-repositories --repository-names ${ECR_REPO_NAME} --region ${AWS_REGION} 2>/dev/null; then
    echo "ECR repository not found. Creating..."
    aws ecr create-repository --repository-name ${ECR_REPO_NAME} --region ${AWS_REGION} || {
        echo "Failed to create ECR repository"
        exit 1
    }
else
    echo "ECR repository already exists."
fi

# Add permissions to ECR repository
echo "Setting ECR repository policy..."
aws ecr set-repository-policy \
    --repository-name ${ECR_REPO_NAME} \
    --region ${AWS_REGION} \
    --policy-text '{
      "Version": "2012-10-17",
      "Statement": [
        {
          "Sid": "LambdaECRImageRetrievalPolicy",
          "Effect": "Allow",
          "Principal": {
            "Service": "lambda.amazonaws.com"
          },
          "Action": [
            "ecr:BatchGetImage",
            "ecr:GetDownloadUrlForLayer"
          ]
        }
      ]
    }' || {
    echo "Failed to set ECR repository policy"
    exit 1
}

# Step 3: Build and Tag Docker Image
echo "Step 3: Building Docker image..."
DOCKER_BUILDKIT=0 docker build --no-cache \
  --platform=linux/amd64 \
  --build-arg LAMBDA_TASK_ROOT=/var/task \
  --build-arg LAMBDA_RUNTIME_DIR=/var/runtime \
  -t ${ECR_REPO_NAME}:latest ./lambdas/ollama_llm || {
    echo "Docker build failed"
    exit 1
}

echo "Tagging image with timestamp ${IMAGE_TAG}..."
docker tag ${ECR_REPO_NAME}:latest ${IMAGE_URI} || {
    echo "Failed to tag Docker image"
    exit 1
}

# Step 4: Push Image to ECR - Added retries
echo "Step 4: Pushing Docker image to ECR..."
MAX_RETRIES=3
RETRY_COUNT=0
PUSH_SUCCESS=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ] && [ "$PUSH_SUCCESS" = false ]; do
    if docker push ${IMAGE_URI}; then
        PUSH_SUCCESS=true
        echo "Push successful!"
    else
        RETRY_COUNT=$((RETRY_COUNT+1))
        if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
            echo "Failed to push after $MAX_RETRIES attempts"
            exit 1
        fi
        echo "Push failed, retrying in 5 seconds... (Attempt $RETRY_COUNT of $MAX_RETRIES)"
        sleep 5
    fi
done

# Step 5: Deploy CloudFormation Stack with error checking
echo "Step 5: Deploying CloudFormation stack..."
if ! aws cloudformation deploy \
    --template-file template.yaml \
    --stack-name ${STACK_NAME} \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides ImageUri=${IMAGE_URI}; then
    
    echo "CloudFormation stack deployment failed. Checking stack events..."
    aws cloudformation describe-stack-events --stack-name ${STACK_NAME}
    exit 1
fi

# Step 6: Wait for stack to complete and get Lambda function name
echo "Step 6: Waiting for stack to stabilize..."
if ! (aws cloudformation wait stack-create-complete --stack-name ${STACK_NAME} || \
      aws cloudformation wait stack-update-complete --stack-name ${STACK_NAME}); then
    echo "Failed waiting for stack to stabilize"
    aws cloudformation describe-stack-events --stack-name ${STACK_NAME}
    exit 1
fi

# Get the actual Lambda function name from CloudFormation stack
echo "Step 7: Getting Lambda function name from stack outputs..."
LAMBDA_FUNCTION_NAME=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --query 'Stacks[0].Outputs[?OutputKey==`FunctionName`].OutputValue' \
    --output text)

if [ -z "$LAMBDA_FUNCTION_NAME" ]; then
    echo "Could not find Lambda function name in stack outputs"
    exit 1
fi

echo "Updating Lambda function: ${LAMBDA_FUNCTION_NAME}"
if ! aws lambda update-function-code \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --image-uri ${IMAGE_URI}; then
    echo "Failed to update Lambda function code"
    exit 1
fi

echo "Deployment completed successfully!"
