# Backend Implementation

I used Cursor AI IDE and I built the whole backend from scratch. These are the steps I followed.

Repo: https://github.com/imsrgadich/free-genai-bootcamp-2025/tree/main/lang-portal/backend

- First I created a detailed (backend technical specification)[https://github.com/imsrgadich/free-genai-bootcamp-2025/blob/main/lang-portal/backend_technical_specs.md], I generously followed the same instructions from the video and Google docs and updated it according to my use case. Then, I asked the LLM to generate me the backend code. It created the backend/ directory and created the necessary modules: main,py, init_db.py, requirements.txt and then created a detailed REAMDE.md to follow-up on. It took few iterations to get the backend working with the current set of API's and database design. 
- Next, I asked the LLM to read the frontend code and create me a (README.md)[https://github.com/imsrgadich/free-genai-bootcamp-2025/blob/main/lang-portal/frontend-react/README.md] to get the frontend working. I followed and got it frontend to work. 
- I started to check the UI and inspecting the elements to see the failed errors and followed along. 
- Additionally, the dashboard endpoint was missing, I had to implement that. 
- I had a lot of CORS errors. It took multiple interations to get the backend working. 
- I got all the endpoints working.

# Frontend implementation

Repo: https://github.com/imsrgadich/free-genai-bootcamp-2025/tree/main/lang-portal/frontend-react

These are the steps I had to follow to get the backend and frontend working

- I had to update the frontend (api.ts)[https://github.com/imsrgadich/free-genai-bootcamp-2025/blob/main/lang-portal/frontend-react/src/services/api.ts] to work according the backend and data design schema. I had to remove Japanese related words and add Hindi related column names. 
- I also had to update the (pages)[https://github.com/imsrgadich/free-genai-bootcamp-2025/tree/main/lang-portal/frontend-react/src/pages] to have the types inline with the database design. 
