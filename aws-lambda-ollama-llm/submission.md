# AWS Lambda Ollama Server Deployment


Repo:https://github.com/imsrgadich/free-genai-bootcamp-2025/tree/main/aws-lambda-ollama-llm

- The project is built on the premise that the lambda function has 10GB of memory but for newly created accounts the maximum memory allocation is 3008MB. I had to default to smaller models like Llama 3.2 1B. I still had issues running the lambda function due to memory constraints.
- Majority of the time was spent get the Dockerfile to work.
    - Had to optimize the Dockerfile to reduce the size of the image by using the staging mechanism.
    - Had issues with type of the Docker image that was created and pushed to ECR. The error was `The image manifest or layer media type for the source image is not supported`. Needed multiple attempts to get the correct Dockerfile for the lambda function. I solved it by using the base docker image from (https://gallery.ecr.aws/)[https://gallery.ecr.aws/].
    - I had issues with entrypoint, as lambda does run python scripts, had to use Lambda RIC and run the subprocess for entrypoint.sh inside the lambda_function.py.
- Used Llama3.2:1b model as I had only 3GB of memory allocated, as mine was new account. 
- Had to heavily update the `deploy.sh` script to automate the deployment process, now it user friendly and easier to use. Implemented error checking and wait times for process to be smooth. 
- I also had issues with setting the correct user permissions, took multiple interations to get the all the permissions. Link: https://github.com/imsrgadich/free-genai-bootcamp-2025/blob/main/aws-lambda-ollama-llm/aws-user-permssions
- Also had to add necessary permissions for ECR repository to be able to interact with Lambda function. The necessary permissions are there in (template.yml)[https://github.com/imsrgadich/free-genai-bootcamp-2025/blob/main/aws-lambda-ollama-llm/template.yaml]