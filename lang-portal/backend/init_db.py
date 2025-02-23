import sqlite3
import os

def init_db():
    # Remove existing database if it exists
    if os.path.exists("lang_portal.db"):
        os.remove("lang_portal.db")

    # Create new database
    conn = sqlite3.connect("lang_portal.db")
    cursor = conn.cursor()

    # Create tables
    cursor.executescript("""
        CREATE TABLE words (
            word_id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_hindi_text TEXT NOT NULL,
            word_english_text TEXT NOT NULL,
            word_meaning TEXT NOT NULL,
            word_part_of_speech TEXT NOT NULL,
            word_origin TEXT,
            example_sentence TEXT
        );

        CREATE TABLE groups (
            group_id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT NOT NULL
        );

        CREATE TABLE words_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id INTEGER,
            group_id INTEGER,
            FOREIGN KEY (word_id) REFERENCES words (word_id),
            FOREIGN KEY (group_id) REFERENCES groups (group_id)
        );

        CREATE TABLE study_activities (
            study_activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            name TEXT NOT NULL,
            FOREIGN KEY (group_id) REFERENCES groups (group_id)
        );

        CREATE TABLE study_sessions (
            study_session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_activity_id INTEGER,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            FOREIGN KEY (study_activity_id) REFERENCES study_activities (study_activity_id)
        );

        CREATE TABLE word_review_items (
            word_review_items_id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_session_id INTEGER,
            word_id INTEGER,
            is_correct BOOLEAN NOT NULL,
            FOREIGN KEY (study_session_id) REFERENCES study_sessions (study_session_id),
            FOREIGN KEY (word_id) REFERENCES words (word_id)
        );
    """)

    # Insert some sample data
    cursor.executescript("""
        INSERT INTO words (word_id, word_hindi_text, word_english_text, word_meaning, word_part_of_speech)
        VALUES 
            (1, 'नमस्ते', 'namaste', 'hello', 'greeting'),
            (2, 'धन्यवाद', 'dhanyavaad', 'thank you', 'expression'),
            (3, 'पानी', 'paani', 'water', 'noun');

        INSERT INTO groups (group_id, group_name)
        VALUES 
            (1, 'Basic Greetings'),
            (2, 'Common Words'),
            (3, 'Expressions');

        INSERT INTO words_groups (id, word_id, group_id)
        VALUES 
            (1, 1, 1),
            (2, 2, 3),
            (3, 3, 2);

        INSERT INTO study_activities (study_activity_id, group_id, name)
        VALUES 
            (1, 1, 'Greetings Quiz'),
            (2, 2, 'Common Words Practice'),
            (3, 3, 'Expressions Review');

        INSERT INTO study_sessions (study_session_id, study_activity_id, start_time, end_time)
        VALUES 
            (1, 1, '2024-01-01 10:00:00', '2024-01-01 10:30:00'),
            (2, 2, '2024-01-01 11:00:00', '2024-01-01 11:30:00'),
            (3, 3, '2024-01-01 12:00:00', '2024-01-01 12:30:00');

        INSERT INTO word_review_items (word_review_items_id, study_session_id, word_id, is_correct)
        VALUES 
            (1, 1, 1, TRUE),
            (2, 2, 2, FALSE),
            (3, 3, 3, TRUE);
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db() 