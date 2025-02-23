import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import sqlite3

from ..main import app, get_db

client = TestClient(app)

# Test database setup
@pytest.fixture
def test_db():
    # Create test database
    db = sqlite3.connect(':memory:')
    db.row_factory = sqlite3.Row
    
    # Create tables
    with open('schema.sql', 'r') as f:
        db.executescript(f.read())
    
    # Insert test data
    cursor = db.cursor()
    
    # Add test words
    cursor.executemany(
        "INSERT INTO words (word_hindi_text, word_english_text, word_meaning, word_part_of_speech) VALUES (?, ?, ?, ?)",
        [
            ("पानी", "water", "liquid essential for life", "noun"),
            ("खाना", "food", "something to eat", "noun"),
            ("सोना", "sleep", "rest at night", "verb")
        ]
    )
    
    # Add test groups
    cursor.executemany(
        "INSERT INTO groups (group_name) VALUES (?)",
        [("Basics",), ("Daily Activities",)]
    )
    
    # Add test study activities
    cursor.executemany(
        "INSERT INTO study_activities (group_id, name) VALUES (?, ?)",
        [(1, "Basic Vocabulary"), (2, "Daily Actions")]
    )
    
    # Add test study sessions
    now = datetime.now()
    cursor.executemany(
        "INSERT INTO study_sessions (study_activity_id, start_time) VALUES (?, ?)",
        [
            (1, now - timedelta(days=2)),
            (1, now - timedelta(days=1)),
            (1, now)
        ]
    )
    
    # Add test word reviews
    cursor.executemany(
        "INSERT INTO word_review_items (study_session_id, word_id, is_correct) VALUES (?, ?, ?)",
        [
            (1, 1, True),
            (1, 2, False),
            (2, 1, True),
            (3, 1, True),
            (3, 2, True)
        ]
    )
    
    db.commit()
    return db

def test_get_dashboard_stats_success(test_db):
    """Test successful retrieval of dashboard stats"""
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_vocabulary"] == 3
    assert data["total_words_studied"] == 2
    assert data["mastered_words"] == 1  # word_id 1 has >80% success
    assert data["success_rate"] == 0.8  # 4 correct out of 5 reviews
    assert data["total_sessions"] == 3
    assert data["active_groups"] == 1
    assert data["current_streak"] == 3

def test_get_dashboard_stats_empty_db(test_db):
    """Test stats with empty database"""
    # Clear all tables
    cursor = test_db.cursor()
    tables = ["word_review_items", "study_sessions", "study_activities", "words", "groups"]
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
    test_db.commit()
    
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_vocabulary"] == 0
    assert data["total_words_studied"] == 0
    assert data["mastered_words"] == 0
    assert data["success_rate"] == 0
    assert data["total_sessions"] == 0
    assert data["active_groups"] == 0
    assert data["current_streak"] == 0

def test_get_dashboard_stats_db_error(monkeypatch):
    """Test handling of database errors"""
    def mock_get_db():
        raise sqlite3.OperationalError("mock db error")
    
    monkeypatch.setattr("main.get_db", mock_get_db)
    
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 503
    assert response.json()["detail"] == "Database connection failed"

def test_get_dashboard_stats_calculation_error(test_db):
    """Test handling of calculation errors"""
    # Corrupt the study_sessions table to cause a calculation error
    cursor = test_db.cursor()
    cursor.execute("ALTER TABLE study_sessions RENAME TO study_sessions_old")
    
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 500
    assert response.json()["detail"] == "Database query failed"
    
    # Restore the table
    cursor.execute("ALTER TABLE study_sessions_old RENAME TO study_sessions") 