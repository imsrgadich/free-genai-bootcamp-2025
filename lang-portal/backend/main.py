from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import sqlite3
import os
import logging
import psutil  # We'll need to add this to requirements.txt
from fastapi.responses import JSONResponse

# Move this to top, after imports
START_TIME = datetime.now()

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Lang Portal API")

# Define allowed origins - include all development ports
origins = [
    "http://localhost:5173",    # Vite frontend
    "http://localhost:8000",    # Our FastAPI port
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
]

# Update CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,  # Keep this False
    allow_methods=["*"],
    allow_headers=["*"]
)

# Database connection helper
def get_db():
    db = sqlite3.connect("lang_portal.db")
    db.row_factory = sqlite3.Row
    return db

# Models - reorder these
class Group(BaseModel):
    group_id: Optional[int] = None
    group_name: str

class Word(BaseModel):
    word_id: Optional[int] = None
    word_hindi_text: str
    word_english_text: str
    word_meaning: str
    word_part_of_speech: str
    word_origin: Optional[str] = None
    example_sentence: Optional[str] = None
    correct_count: Optional[int] = 0
    wrong_count: Optional[int] = 0
    word_groups: Optional[List[Group]] = None

class StudyActivity(BaseModel):
    study_activity_id: Optional[int] = None
    group_id: int
    name: str

class StudySession(BaseModel):
    study_session_id: Optional[int] = None
    study_activity_id: int
    start_time: datetime
    end_time: Optional[datetime] = None

class WordReviewItem(BaseModel):
    word_review_items_id: Optional[int] = None
    study_session_id: int
    word_id: int
    is_correct: bool

class DashboardStats(BaseModel):
    total_vocabulary: int        # Total words in system
    total_words_studied: int     # Unique words reviewed
    mastered_words: int         # Words with >80% success
    success_rate: float         # Overall correct rate
    total_sessions: int         # Total study sessions
    active_groups: int          # Groups used in last 30 days
    current_streak: int         # Consecutive days studied

# Add this model for the request
class CreateStudySessionRequest(BaseModel):
    group_id: int
    study_activity_id: int

# API Endpoints

# Words endpoints
@app.get("/api/words")
async def get_words(
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc",
    page: int = 1,
    page_size: int = 10
):
    """Get paginated words with review statistics"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Validate sort parameters
        valid_sort_columns = [
            "word_id", 
            "word_hindi_text",  # Changed from kanji
            "word_english_text",
            "word_meaning",
            "word_part_of_speech"
        ]
        if sort_by and sort_by not in valid_sort_columns:
            sort_by = "word_hindi_text"  # Default sort column
        
        # Build base query
        base_query = """
            SELECT 
                w.*,
                COUNT(CASE WHEN wri.is_correct THEN 1 END) as correct_count,
                COUNT(CASE WHEN NOT wri.is_correct THEN 1 END) as wrong_count
            FROM words w
            LEFT JOIN word_review_items wri ON w.word_id = wri.word_id
        """
        count_query = "SELECT COUNT(*) FROM words"
        where_clause = ""
        params = []
        
        # Add search condition if provided
        if search:
            where_clause = " WHERE word_hindi_text LIKE ? OR word_english_text LIKE ?"
            params.extend([f"%{search}%", f"%{search}%"])
        
        # Get total count
        cursor.execute(count_query + where_clause, params)
        total_count = cursor.fetchone()[0]
        
        # Build final query
        query = base_query + where_clause + " GROUP BY w.word_id"
        
        # Add sorting
        if sort_by:
            query += f" ORDER BY {sort_by} {sort_order}"
            
        # Add pagination
        query += " LIMIT ? OFFSET ?"
        params.extend([page_size, (page - 1) * page_size])
        
        # Execute query
        cursor.execute(query, params)
        words = [dict(row) for row in cursor.fetchall()]
        
        # Calculate total pages
        total_pages = (total_count + page_size - 1) // page_size
        
        return {
            "items": words,
            "total": total_count,
            "page": page,
            "per_page": page_size,
            "total_pages": total_pages
        }
        
    except sqlite3.Error as e:
        logger.error(f"Database error in words: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch words"
        )
    finally:
        db.close()

@app.get("/api/words/{word_id}", response_model=Word)
async def get_word(word_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM words WHERE word_id = ?", (word_id,))
    word = cursor.fetchone()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    return dict(word)

@app.post("/api/words", response_model=Word)
async def create_word(word: Word):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO words (word_hindi_text, word_english_text, word_meaning, word_part_of_speech)
        VALUES (?, ?, ?, ?)
        RETURNING *
    """, (word.word_hindi_text, word.word_english_text, word.word_meaning, word.word_part_of_speech))
    db.commit()
    return dict(cursor.fetchone())

@app.put("/api/words/{word_id}", response_model=Word)
async def update_word(word_id: int, word: Word):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE words 
        SET word_hindi_text = ?, word_english_text = ?, word_meaning = ?, word_part_of_speech = ?
        WHERE word_id = ?
        RETURNING *
    """, (word.word_hindi_text, word.word_english_text, word.word_meaning, word.word_part_of_speech, word_id))
    db.commit()
    updated_word = cursor.fetchone()
    if not updated_word:
        raise HTTPException(status_code=404, detail="Word not found")
    return dict(updated_word)

@app.delete("/api/words/{word_id}")
async def delete_word(word_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM words WHERE word_id = ?", (word_id,))
    db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Word not found")
    return {"message": "Word deleted successfully"}

# Groups endpoints
@app.get("/api/groups", response_model=List[Group])
async def get_groups():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM groups")
    groups = [dict(row) for row in cursor.fetchall()]
    return groups

@app.get("/api/groups/{group_id}", response_model=Group)
async def get_group(group_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,))
    group = cursor.fetchone()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return dict(group)

@app.get("/api/groups/{group_id}/words", response_model=List[Word])
async def get_group_words(group_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT w.* FROM words w
        JOIN words_groups wg ON w.word_id = wg.word_id
        WHERE wg.group_id = ?
    """, (group_id,))
    words = [dict(row) for row in cursor.fetchall()]
    return words

@app.post("/api/groups/{group_id}/words")
async def add_word_to_group(group_id: int, word_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO words_groups (word_id, group_id)
        VALUES (?, ?)
    """, (word_id, group_id))
    db.commit()
    return {"message": "Word added to group successfully"}

@app.delete("/api/groups/{group_id}/words/{word_id}")
async def remove_word_from_group(group_id: int, word_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        DELETE FROM words_groups 
        WHERE group_id = ? AND word_id = ?
    """, (group_id, word_id))
    db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Word not found in group")
    return {"message": "Word removed from group successfully"}

# Study Activities endpoints
@app.get("/api/study-activities")
async def get_study_activities():
    """Get all study activities"""
    logger.info("Fetching study activities")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT 
                study_activity_id,
                group_id,
                name
            FROM study_activities
            ORDER BY name
        """)
        
        activities = [
            {
                "id": row[0],
                "group_id": row[1],
                "name": row[2]
            }
            for row in cursor.fetchall()
        ]
        
        logger.info(f"Found {len(activities)} study activities")
        return activities
        
    except Exception as e:
        logger.error(f"Error fetching study activities: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch study activities"
        )
    finally:
        db.close()

@app.get("/api/study-activities/{activity_id}", response_model=StudyActivity)
async def get_study_activity(activity_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM study_activities WHERE study_activity_id = ?", (activity_id,))
    activity = cursor.fetchone()
    if not activity:
        raise HTTPException(status_code=404, detail="Study activity not found")
    return dict(activity)

@app.get("/api/study-activities/{activity_id}/words", response_model=List[Word])
async def get_activity_words(activity_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT w.* FROM words w
        JOIN words_groups wg ON w.word_id = wg.word_id
        JOIN study_activities sa ON wg.group_id = sa.group_id
        WHERE sa.study_activity_id = ?
    """, (activity_id,))
    words = [dict(row) for row in cursor.fetchall()]
    return words

@app.get("/api/study-activities/{activity_id}/launch")
async def get_activity_launch_data(activity_id: int):
    """Get activity details and available groups for launching"""
    logger.info(f"Fetching launch data for activity {activity_id}")
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # First get the activity details
        cursor.execute("""
            SELECT 
                study_activity_id as id,
                name as title,
                'http://localhost:5173/activities/' || study_activity_id || '/play' as launch_url,
                'http://localhost:5173/activities/' || study_activity_id || '/preview' as preview_url
            FROM study_activities 
            WHERE study_activity_id = ?
        """, (activity_id,))
        
        activity = cursor.fetchone()
        if not activity:
            raise HTTPException(status_code=404, detail="Study activity not found")
            
        # Get all available groups
        cursor.execute("""
            SELECT 
                group_id as id,
                group_name as name
            FROM groups
            ORDER BY group_name
        """)
        
        groups = [dict(row) for row in cursor.fetchall()]
        
        return {
            "activity": dict(activity),
            "groups": groups
        }
        
    except sqlite3.Error as e:
        logger.error(f"Database error in activity launch: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch activity launch data"
        )
    finally:
        db.close()

# Study Sessions endpoints
@app.get("/api/study-sessions")
async def get_study_sessions(
    page: int = 1,
    per_page: int = 10,
    sort_by: str = "start_time",
    order: str = "desc"
):
    """Get paginated study sessions with related info"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Validate sort parameters
        valid_sort_fields = ["study_session_id", "start_time", "end_time", "group_name", "activity_name"]
        if sort_by not in valid_sort_fields:
            sort_by = "start_time"
        if order.lower() not in ["asc", "desc"]:
            order = "desc"
            
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get total count
        cursor.execute("""
            SELECT COUNT(DISTINCT ss.study_session_id)
            FROM study_sessions ss
            JOIN study_activities sa ON ss.study_activity_id = sa.study_activity_id
            JOIN groups g ON sa.group_id = g.group_id
        """)
        total_count = cursor.fetchone()[0]
        
        # Get paginated sessions
        cursor.execute(f"""
            SELECT 
                ss.study_session_id as id,
                sa.group_id,
                g.group_name,
                sa.study_activity_id as activity_id,
                sa.name as activity_name,
                ss.start_time,
                ss.end_time,
                COUNT(wri.word_review_items_id) as review_items_count
            FROM study_sessions ss
            JOIN study_activities sa ON ss.study_activity_id = sa.study_activity_id
            JOIN groups g ON sa.group_id = g.group_id
            LEFT JOIN word_review_items wri ON ss.study_session_id = wri.study_session_id
            GROUP BY ss.study_session_id
            ORDER BY {sort_by} {order}
            LIMIT ? OFFSET ?
        """, (per_page, offset))
        
        sessions = [dict(row) for row in cursor.fetchall()]
        
        # Calculate total pages
        total_pages = (total_count + per_page - 1) // per_page
        
        return {
            "items": sessions,
            "total": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
        
    except sqlite3.Error as e:
        logger.error(f"Database error in study sessions: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch study sessions"
        )
    finally:
        db.close()

@app.get("/api/sessions/{session_id}", response_model=StudySession)
async def get_study_session(session_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT ss.*, sa.name as activity_name, g.group_name,
               COUNT(wri.word_review_items_id) as review_items_count
        FROM study_sessions ss
        JOIN study_activities sa ON ss.study_activity_id = sa.study_activity_id
        JOIN groups g ON sa.group_id = g.group_id
        LEFT JOIN word_review_items wri ON ss.study_session_id = wri.study_session_id
        WHERE ss.study_session_id = ?
        GROUP BY ss.study_session_id
    """, (session_id,))
    session = cursor.fetchone()
    if not session:
        raise HTTPException(status_code=404, detail="Study session not found")
    return dict(session)

@app.post("/api/study-sessions")
async def create_study_session(request: CreateStudySessionRequest):
    """Create a new study session"""
    logger.info(f"Creating study session for group {request.group_id} and activity {request.study_activity_id}")
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            INSERT INTO study_sessions (study_activity_id, start_time)
            VALUES (?, datetime('now'))
            RETURNING study_session_id
        """, (request.study_activity_id,))
        
        session_id = cursor.fetchone()[0]
        db.commit()
        
        return {"session_id": session_id}
        
    except sqlite3.Error as e:
        logger.error(f"Database error creating session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to create study session"
        )
    finally:
        db.close()

@app.put("/api/sessions/{session_id}", response_model=StudySession)
async def update_study_session(session_id: int, session: StudySession):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE study_sessions 
        SET end_time = ?
        WHERE study_session_id = ?
        RETURNING *
    """, (session.end_time, session_id))
    db.commit()
    updated_session = cursor.fetchone()
    if not updated_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return dict(updated_session)

@app.get("/api/sessions/{session_id}/review-items", response_model=List[WordReviewItem])
async def get_session_review_items(session_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT * FROM word_review_items
        WHERE study_session_id = ?
    """, (session_id,))
    items = [dict(row) for row in cursor.fetchall()]
    return items

# Word Review Items endpoints
@app.post("/api/sessions/{session_id}/review-items")
async def create_word_review_item(session_id: int, review_item: WordReviewItem):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO word_review_items (study_session_id, word_id, is_correct)
        VALUES (?, ?, ?)
    """, (session_id, review_item.word_id, review_item.is_correct))
    db.commit()
    return {"message": "Review item created successfully"}

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    logger.info("Starting dashboard stats calculation")
    start_time = datetime.now()

    try:
        db = get_db()
        logger.debug("Database connection established")
        cursor = db.cursor()
        
        # Combine multiple stats in a single query for better performance
        cursor.execute("""
            WITH word_stats AS (
                SELECT 
                    COUNT(DISTINCT word_id) as total_words_studied,
                    COALESCE(AVG(CASE WHEN is_correct THEN 1 ELSE 0 END), 0) as success_rate,
                    (
                        SELECT COUNT(*)
                        FROM (
                            SELECT word_id
                            FROM word_review_items
                            GROUP BY word_id
                            HAVING AVG(CASE WHEN is_correct THEN 1 ELSE 0 END) >= 0.8
                        )
                    ) as mastered_words
                FROM word_review_items
            ),
            session_stats AS (
                SELECT 
                    COUNT(*) as total_sessions,
                    COUNT(DISTINCT g.group_id) as active_groups
                FROM study_sessions ss
                JOIN study_activities sa ON ss.study_activity_id = sa.study_activity_id
                JOIN groups g ON sa.group_id = g.group_id
                WHERE ss.start_time >= date('now', '-30 days')
            )
            SELECT 
                (SELECT COUNT(*) FROM words) as total_vocabulary,
                ws.total_words_studied,
                ws.mastered_words,
                ws.success_rate,
                ss.total_sessions,
                ss.active_groups,
                (
                    WITH RECURSIVE dates AS (
                        SELECT date(start_time) as study_date,
                               date(start_time, '-1 day') as prev_date
                        FROM study_sessions
                        GROUP BY date(start_time)
                        ORDER BY study_date DESC
                        LIMIT 1
                        
                        UNION ALL
                        
                        SELECT d.prev_date,
                               date(d.prev_date, '-1 day')
                        FROM dates d
                        JOIN study_sessions ss 
                        ON date(ss.start_time) = d.prev_date
                        GROUP BY d.prev_date
                    )
                    SELECT COUNT(*) FROM dates
                ) as current_streak
            FROM word_stats ws, session_stats ss
        """)
        
        result = cursor.fetchone()
        stats = {
            "total_vocabulary": result[0],
            "total_words_studied": result[1],
            "mastered_words": result[2],
            "success_rate": float(result[3]),
            "total_sessions": result[4],
            "active_groups": result[5],
            "current_streak": result[6]
        }
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Dashboard stats calculated successfully in {duration:.2f} seconds")
        
        return stats
        
    except sqlite3.OperationalError as e:
        logger.error(f"Database query failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Database query failed"
        )
    except sqlite3.Error as e:
        logger.error(f"SQLite error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"Unexpected error calculating dashboard stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to calculate dashboard statistics"
        )
    finally:
        db.close()
        logger.debug("Database connection closed")

# Add these new endpoints
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/system/stats")
async def system_stats():
    """System monitoring endpoint"""
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "uptime": datetime.now() - START_TIME
    }

@app.get("/api/system/db-stats")
async def db_stats():
    """Database statistics"""
    db = get_db()
    cursor = db.cursor()
    try:
        stats = {
            "total_words": cursor.execute("SELECT COUNT(*) FROM words").fetchone()[0],
            "total_sessions": cursor.execute("SELECT COUNT(*) FROM study_sessions").fetchone()[0],
            "total_reviews": cursor.execute("SELECT COUNT(*) FROM word_review_items").fetchone()[0],
            "db_size": os.path.getsize("lang_portal.db") / (1024 * 1024)  # Size in MB
        }
        return stats
    finally:
        db.close()

@app.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats_alt():
    """Alternative route for dashboard stats"""
    return await get_dashboard_stats()

@app.get("/dashboard/recent-session")
async def get_recent_session():
    """Get most recent study session with stats"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            SELECT 
                ss.study_session_id as id,
                sa.group_id,
                sa.name as activity_name,
                ss.start_time as created_at,
                SUM(CASE WHEN wri.is_correct THEN 1 ELSE 0 END) as correct_count,
                SUM(CASE WHEN NOT wri.is_correct THEN 1 ELSE 0 END) as wrong_count
            FROM study_sessions ss
            JOIN study_activities sa ON ss.study_activity_id = sa.study_activity_id
            LEFT JOIN word_review_items wri ON ss.study_session_id = wri.study_session_id
            GROUP BY ss.study_session_id
            ORDER BY ss.start_time DESC
            LIMIT 1
        """)
        
        session = cursor.fetchone()
        if not session:
            return None
            
        return {
            "id": session[0],
            "group_id": session[1],
            "activity_name": session[2],
            "created_at": session[3],
            "correct_count": session[4] or 0,
            "wrong_count": session[5] or 0
        }
        
    except sqlite3.Error as e:
        logger.error(f"Database error in recent session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch recent session"
        )
    finally:
        db.close()

# Add alternative routes without /api prefix
@app.get("/words", response_model=List[Word])
async def get_words_alt(
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc",
    page: int = 1,
    page_size: int = 10
):
    return await get_words(search, sort_by, sort_order, page, page_size)

@app.get("/groups", response_model=List[Group])
async def get_groups_alt():
    return await get_groups()

@app.get("/api/study-sessions/{session_id}")
async def get_study_session_details(session_id: int):
    """Get details of a specific study session"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT 
                ss.study_session_id as id,
                sa.group_id,
                g.group_name,
                sa.study_activity_id as activity_id,
                sa.name as activity_name,
                ss.start_time,
                ss.end_time,
                COUNT(wri.word_review_items_id) as review_items_count
            FROM study_sessions ss
            JOIN study_activities sa ON ss.study_activity_id = sa.study_activity_id
            JOIN groups g ON sa.group_id = g.group_id
            LEFT JOIN word_review_items wri ON ss.study_session_id = wri.study_session_id
            WHERE ss.study_session_id = ?
            GROUP BY ss.study_session_id
        """, (session_id,))
        
        session = cursor.fetchone()
        if not session:
            raise HTTPException(status_code=404, detail="Study session not found")
            
        return dict(session)
        
    except sqlite3.Error as e:
        logger.error(f"Database error fetching session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch study session")
    finally:
        db.close() 