# Backend Server Technical Specifications

## Business Goal
A language learning school, Basha Bol, a Hindi language based  wants to build a prototype of learning portal which will act as three things:
- A store for all the vocabulary that can be learned.
- A Learning record store (LRS), providing comprehensive learning analytics and improvement suggestions.
- A single stop-shop for various language learning based games.

## Technical Specifications

- Use SQLite3 as the database
- Use Python and FastAPI to build the backend server
    - FastAPI's async capabilities will be beneficial when processing learning analytics data, especially as your dataset grows
- Does not require authentication/authorization, assume there is a single user
- Use the local machine as the server and also, try to deploy it on an Azure instance.

## Database Design
### Tables

### Words 

Table for stored vocabulary for a language.

| Column Name | Type | Description |
|------------|------|-------------|
| word_id | integer | unique identifier for the word |
| word_hindi_text | string | text of the word in Hindi |
| word_english_text | string | text of the word in English |
| word_meaning | string | meaning of the word |
| word_part_of_speech | string | part of speech of the word |

### words_groups

Table for joint table for words and groups

| Column Name | Type | Description |
|-------------|------|-------------|
| id | integer | unique identifier for the joint table |
| word_id | integer | unique identifier for the word |
| group_id | string | unique identifier for the group |

### groups

Table for list of groups

| Column Name | Type | Description |
|-------------|------|-------------|
| group_id | integer | unique identifier for the group |
| group_name | string | name of the group |

### study_activities

Table for list of activities for a study session linking a study session to a group. 

| Column Name | Type | Description |
|-------------|------|-------------|
| study_activity_id | integer | unique identifier for the study activity |
| group_id | string | unique identifier for the group |
| name | string | name of the study activity |

### study_sessions

Table for record of study sessions grouping word_review_items

| Column Name | Type | Description |
|-------------|------|-------------|
| study_session_id | integer | unique identifier for the study session |
| study_activity_id | integer | unique identifier for the study activity |
| start_time | datetime | start time of the study session |
| end_time | datetime | end time of the study session |

### word_review_items

Table for a record of word practice, determining if the word was correct or not. 

| Column Name | Type | Description |
|-------------|------|-------------|
| word_review_items_id | integer | unique identifier for the word review item |
| study_session_id | integer | unique identifier for the study session |
| word_id | integer | unique identifier for the word |
| is_correct | boolean | whether the word was correct or not |

### API Endpoints
---

#### Word API Endpoints
GET /api/words
- Query params: 
  - search (optional): Search by hindi or english text
  - sort_by (optional): Field to sort by
  - sort_order (optional): 'asc' or 'desc'
  - page: Page number
  - page_size: Items per page
- Returns: List of words with pagination

GET /api/words/{word_id}
- Returns: Single word details

POST /api/words
- Body: Word object
- Returns: Created word

PUT /api/words/{word_id}
- Body: Word object
- Returns: Updated word

DELETE /api/words/{word_id}
- Returns: Success message

#### Group API Endpoints

GET /api/groups
- Returns: List of all groups

GET /api/groups/{group_id}
- Returns: Single group details

GET /api/groups/{group_id}/words
- Returns: List of words in the group

POST /api/groups
- Body: Group object
- Returns: Created group

PUT /api/groups/{group_id}
- Body: Group object
- Returns: Updated group

POST /api/groups/{group_id}/words
- Body: { word_id: number }
- Returns: Added word to group

DELETE /api/groups/{group_id}/words/{word_id}
- Returns: Removed word from group

#### Study Activity API Endpoints

GET /api/study-activities
- Returns: List of all study activities

GET /api/study-activities/{activity_id}
- Returns: Single study activity details

POST /api/study-activities
- Body: StudyActivity object
- Returns: Created study activity

PUT /api/study-activities/{activity_id}
- Body: StudyActivity object
- Returns: Updated study activity

DELETE /api/study-activities/{activity_id}
- Returns: Success message

GET /api/study-activities/{activity_id}/words
- Returns: List of words for the activity (based on group)

#### Study Session API Endpoints

GET /api/sessions
- Query params:
  - sort_by (optional)
  - sort_order (optional): 'asc' or 'desc'
- Returns: List of study sessions with activity and group info

GET /api/sessions/{session_id}
- Returns: Single session details with related info

POST /api/sessions
- Body: StudySession object
- Returns: Created session

PUT /api/sessions/{session_id}
- Body: StudySession object (for updating end_time)
- Returns: Updated session

GET /api/sessions/{session_id}/review-items
- Returns: List of word review items for the session

POST /api/sessions/{session_id}/review-items
- Body: WordReviewItem object
- Returns: Created review item

#### Dashboard API Endpoints

GET /api/dashboard/stats
- Returns: Dashboard statistics including:
  ```json
  {
    "total_vocabulary": "Total number of words in system",
    "total_words_studied": "Number of unique words reviewed",
    "mastered_words": "Words with >80% success rate",
    "success_rate": "Overall success rate (0-1)",
    "total_sessions": "Total number of study sessions",
    "active_groups": "Groups with activity in last 30 days",
    "current_streak": "Consecutive days with study sessions"
  }
  ```
- Success Response (200):
  ```json
  {
    "total_vocabulary": 100,
    "total_words_studied": 50,
    "mastered_words": 20,
    "success_rate": 0.75,
    "total_sessions": 10,
    "active_groups": 3,
    "current_streak": 5
  }
  ```
- Error Responses:
  - 500: Database query failed
  - 503: Database connection failed

Notes:
- Success rate is calculated as (correct answers) / (total answers)
- Mastered words have a success rate >= 80%
- Active groups are those with study sessions in the last 30 days
- Current streak counts consecutive days with at least one study session

### Vocabulary Store


### Learning Record Store


### Game Launcher





