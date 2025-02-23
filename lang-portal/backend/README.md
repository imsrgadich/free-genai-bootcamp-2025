# Lang Portal Backend

This is the backend service for the Lang Portal application, built using FastAPI. It provides a RESTful API for managing words, groups, study activities, study sessions, and word review items.

## Prerequisites

- Python 3.7+
- SQLite (for database management)

## Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd lang-portal/backend
   ```

2. **Create a virtual environment:**

   ```bash
   conda create --name lang-portal python=3.12.9
   ```

3. **Activate the virtual environment:**

   ```bash
   conda activate lang-portal
   ```

4. **Install the dependencies:**

   ```bash
   sed -i '/sqlite3/d' lang-portal/backend/requirements.txt && pip install -r lang-portal/backend/requirements.txt
   ```

## Database Initialization

Before running the application, initialize the database:
```bash
python init_db.py
```

This will create a new SQLite database (`lang_portal.db`) and populate it with sample data.

## Running the Application

To start the FastAPI server, use the following command:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

- The application will be accessible at `http://localhost:8000`.
- The API documentation is available at `http://localhost:8000/docs`.

## API Endpoints

The backend provides the following API endpoints:

- **Words**
  - `GET /api/words`: Retrieve a list of words.
  - `GET /api/words/{word_id}`: Retrieve a specific word by ID.
  - `POST /api/words`: Create a new word.
  - `PUT /api/words/{word_id}`: Update an existing word.
  - `DELETE /api/words/{word_id}`: Delete a word.

- **Groups**
  - `GET /api/groups`: Retrieve a list of groups.
  - `GET /api/groups/{group_id}`: Retrieve a specific group by ID.
  - `GET /api/groups/{group_id}/words`: Retrieve words in a specific group.
  - `POST /api/groups/{group_id}/words`: Add a word to a group.
  - `DELETE /api/groups/{group_id}/words/{word_id}`: Remove a word from a group.

- **Study Activities**
  - `GET /api/study-activities`: Retrieve a list of study activities.
  - `GET /api/study-activities/{activity_id}`: Retrieve a specific study activity by ID.
  - `GET /api/study-activities/{activity_id}/words`: Retrieve words associated with a study activity.

- **Study Sessions**
  - `GET /api/sessions`: Retrieve a list of study sessions.
  - `GET /api/sessions/{session_id}`: Retrieve a specific study session by ID.
  - `POST /api/sessions`: Create a new study session.
  - `PUT /api/sessions/{session_id}`: Update an existing study session.
  - `GET /api/sessions/{session_id}/review-items`: Retrieve review items for a study session.

- **Word Review Items**
  - `POST /api/sessions/{session_id}/review-items`: Create a new word review item.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

# Deployment Instructions

## Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload
```

## Production Deployment
```bash
# Build Docker image
docker build -t lang-portal-api .

# Run container
docker run -d -p 8000:8000 lang-portal-api

# Deploy to Kubernetes
kubectl apply -f deployment.yaml
```

## Monitoring
The following endpoints are available for monitoring:
- `/health` - Basic health check
- `/api/system/stats` - System resource usage
- `/api/system/db-stats` - Database statistics

## Logs
Logs are written to `app.log` and stdout. Monitor them using:
```bash
# Docker logs
docker logs -f <container_id>

# Kubernetes logs
kubectl logs -f deployment/lang-portal-api
```
