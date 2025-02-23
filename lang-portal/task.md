# Backend — Lang Portal

## Difficulty: Level 200

### Business Goal 
A language learning school wants to build a prototype of learning portal which will act as three things:
- Inventory of possible vocabulary that can be learned
- Act as a Learning record store (LRS), providing correct and wrong score on practice vocabulary
- A unified launchpad to launch different learning apps

You have been tasked with creating the backend API of the application.

### Technical Restrictions
- Use SQLite3 as the database
- You can use any language or framework 
- Does not require authentication/authorization, assume there is a single user

### Leverage AI-coding assistants to write your backend code:
- Cursor
- Windsurf Codeium
- Github Copilot
- Amazon Q Developer
- Google Code Assist

## Technical Specification

### Routes

#### GET /words
Get paginated list of words with review statistics
- **Parameters:**
  - `page`: Page number (default: 1)
  - `sort_by`: Sort field ('kanji', 'romaji', 'english', 'correct_count', 'wrong_count') (default: 'kanji')
  - `order`: Sort order ('asc' or 'desc') (default: 'asc')

#### GET /groups 
Get paginated list of word groups with word counts

#### GET /groups/:id
Get words from a specific group (This is intended to be used by target apps)
- **Parameters:**
  - `page`: Page number (default: 1)
  - `sort_by`: Sort field ('name', 'words_count') (default: 'name')
  - `order`: Sort order ('asc' or 'desc') (default: 'asc')

#### POST /studysessions
Create a new study session for a group
- **Parameters:**
  - `group_id`: ID of the group to study (required)
  - `study_activity_id`: ID of the study activity (required)

#### POST /study-sessions/:id/review
Log a review attempt for a word during a study session

### Database Schema 

#### words
Stores individual Japanese vocabulary words.
- `id` (Primary Key): Unique identifier for each word
- `kanji` (String, Required): The word written in Japanese kanji
- `romaji` (String, Required): Romanized version of the word
- `english` (String, Required): English translation of the word
- `parts` (JSON, Required): Word components stored in JSON format

#### groups
Manages collections of words.
- `id` (Primary Key): Unique identifier for each group
- `name` (String, Required): Name of the group
- `words_count` (Integer, Default: 0): Counter cache for the number of words in the group

#### word_groups
Join-table enabling many-to-many relationship between words and groups.
- `word_id` (Foreign Key): References words.id
- `group_id` (Foreign Key): References groups.id

#### study_activities
Defines different types of study activities available.
- `id` (Primary Key): Unique identifier for each activity
- `name` (String, Required): Name of the activity (e.g., "Flashcards", "Quiz")
- `url` (String, Required): The full URL of the study activity

#### study_sessions
Records individual study sessions.
- `id` (Primary Key): Unique identifier for each session
- `group_id` (Foreign Key): References groups.id
- `study_activity_id` (Foreign Key): References study_activities.id
- `created_at` (Timestamp, Default: Current Time): When the session was created

#### word_review_items
Tracks individual word reviews within study sessions.
- `id` (Primary Key): Unique identifier for each review
- `word_id` (Foreign Key): References words.id
- `study_session_id` (Foreign Key): References study_sessions.id
- `correct` (Boolean, Required): Whether the answer was correct
- `created_at` (Timestamp, Default: Current Time): When the review occurred

### Relationships

- word belongs to groups through word_groups
- group belongs to words through word_groups
- session belongs to a group
- session belongs to a study_activity
- session has many word_review_items
- word_review_item belongs to a study_session
- word_review_item belongs to a word

### Design Notes
- All tables use auto-incrementing primary keys
- Timestamps are automatically set on creation where applicable
- Foreign key constraints maintain referential integrity
- JSON storage for word parts allows flexible component storage
- Counter cache on groups.words_count optimizes word counting queries

### Home Challenge
- Level 1: reimplement the missing API endpoints
- Level 5: rebuild the entire thing from scratch with whatever you want.

## Technical uncertainty

### Backend implementation
- Reimplemented the backend in Python using FastAPI. 
- Used SQLite3 for the database.
- I used Cursor IDE with "claude 3.5 sonnet" to write the code.
- Once I had the technical specs, coding with Cursor was a breeze.
- Had no clear understanding of how frontend will communicate with the backend.

