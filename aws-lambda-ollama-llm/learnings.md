- The project is built on the premise that the lambda function has 10GB of memory but for newly created accounts the maximum memory allocation is 3008MB. I had to default to smaller models like Llama 3.2 1B. I still had issues running the lambda function due to memory constraints.
- Majority of the time was spent get the Dockerfile to work.
    - Had to optimize the Dockerfile to reduce the size of the image.
    - Had issues with type of the Docker image that was created and pushed to ECR. The error was `The image manifest or layer media type for the source image is not supported`. Needed multiple attempts to get the correct Dockerfile for the lambda function.
- Had to heavily update the `deploy.sh` script to automate the deployment process, now it user friendly and easier to use.