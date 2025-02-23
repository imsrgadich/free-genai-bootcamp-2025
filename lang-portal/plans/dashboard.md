# Dashboard Stats API Implementation Plan

## Overview
Implement a new endpoint `/api/dashboard/stats` that provides statistics for the dashboard view, including vocabulary progress, study sessions, and streaks.

## 1. Model Definition
```python
class DashboardStats(BaseModel):
    total_vocabulary: int        # Total words in system
    total_words_studied: int     # Unique words reviewed
    mastered_words: int         # Words with >80% success
    success_rate: float         # Overall correct rate
    total_sessions: int         # Total study sessions
    active_groups: int          # Groups used in last 30 days
    current_streak: int         # Consecutive days studied
```

## 2. SQL Queries Implementation

### a) Total Vocabulary Count
```sql
SELECT COUNT(*) FROM words
```

### b) Total Words Studied
```sql
SELECT COUNT(DISTINCT word_id) 
FROM word_review_items
```

### c) Mastered Words (>80% success)
```sql
SELECT COUNT(*) FROM (
    SELECT word_id,
    AVG(CASE WHEN is_correct THEN 1 ELSE 0 END) as success_rate
    FROM word_review_items
    GROUP BY word_id
    HAVING success_rate >= 0.8
)
```

### d) Success Rate
```sql
SELECT COALESCE(AVG(CASE WHEN is_correct THEN 1 ELSE 0 END), 0)
FROM word_review_items
```

### e) Total Sessions
```sql
SELECT COUNT(*) FROM study_sessions
```

### f) Active Groups (30 days)
```sql
SELECT COUNT(DISTINCT g.group_id)
FROM groups g
JOIN study_activities sa ON g.group_id = sa.group_id
JOIN study_sessions ss ON sa.study_activity_id = ss.study_activity_id
WHERE ss.start_time >= date('now', '-30 days')
```

### g) Current Streak
```sql
WITH RECURSIVE dates AS (
    -- Get most recent study date
    SELECT date(start_time) as study_date,
           date(start_time, '-1 day') as prev_date
    FROM study_sessions
    GROUP BY date(start_time)
    ORDER BY study_date DESC
    LIMIT 1
    
    UNION ALL
    
    -- Recursively get previous consecutive days
    SELECT d.prev_date,
           date(d.prev_date, '-1 day')
    FROM dates d
    JOIN study_sessions ss 
    ON date(ss.start_time) = d.prev_date
    GROUP BY d.prev_date
)
SELECT COUNT(*) FROM dates
```

## 3. Implementation Steps

1. [ ] Add DashboardStats model to main.py
2. [ ] Create new endpoint `/api/dashboard/stats`
3. [ ] Implement each statistic query
4. [ ] Add error handling and logging
5. [ ] Test endpoint with sample data
6. [ ] Update API documentation

## 4. Error Handling
- Handle database connection errors
- Handle empty tables/no data scenarios
- Add appropriate error messages
- Log errors for debugging

## 5. Testing Plan

### Unit Tests
- [ ] Test each stat calculation separately
- [ ] Test with empty database
- [ ] Test with sample data
- [ ] Test edge cases (no sessions, perfect scores, etc.)

### Integration Tests
- [ ] Test endpoint with frontend
- [ ] Verify response format matches frontend expectations
- [ ] Test performance with large datasets

### Test Cases
1. Empty database
   ```json
   {
     "total_vocabulary": 0,
     "total_words_studied": 0,
     "mastered_words": 0,
     "success_rate": 0,
     "total_sessions": 0,
     "active_groups": 0,
     "current_streak": 0
   }
   ```

2. Sample data
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

## 6. API Documentation Update
Add to backend_technical_specs.md:
```markdown
GET /api/dashboard/stats
- Returns: Dashboard statistics including:
  - total_vocabulary: Total number of words in system
  - total_words_studied: Number of unique words reviewed
  - mastered_words: Words with >80% success rate
  - success_rate: Overall success rate (0-1)
  - total_sessions: Total number of study sessions
  - active_groups: Groups with activity in last 30 days
  - current_streak: Consecutive days with study sessions
```

## 7. Performance Considerations
- [ ] Add indexes for frequently queried columns
- [ ] Consider caching for expensive calculations
- [ ] Monitor query execution time
- [ ] Plan for database scaling

## 8. Future Improvements
- Add time period filtering (weekly/monthly stats)
- Add more detailed success metrics
- Cache results for faster dashboard loading
- Add user-specific stats when multi-user support is added

## Implementation Checklist
- [ ] Add DashboardStats model
- [ ] Implement endpoint with basic queries
- [ ] Add error handling
- [ ] Add logging
- [ ] Write tests
- [ ] Update documentation
- [ ] Test with frontend
- [ ] Review and optimize queries
- [ ] Deploy and monitor

## Code Implementation
The endpoint will be implemented in `main.py` as:

```python
@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Get total vocabulary
        cursor.execute("SELECT COUNT(*) FROM words")
        total_vocabulary = cursor.fetchone()[0]
        
        # Get total words studied
        cursor.execute("SELECT COUNT(DISTINCT word_id) FROM word_review_items")
        total_words_studied = cursor.fetchone()[0]
        
        # Get mastered words
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT word_id,
                AVG(CASE WHEN is_correct THEN 1 ELSE 0 END) as success_rate
                FROM word_review_items
                GROUP BY word_id
                HAVING success_rate >= 0.8
            )
        """)
        mastered_words = cursor.fetchone()[0]
        
        # Get success rate
        cursor.execute("""
            SELECT COALESCE(AVG(CASE WHEN is_correct THEN 1 ELSE 0 END), 0)
            FROM word_review_items
        """)
        success_rate = cursor.fetchone()[0]
        
        # Get total sessions
        cursor.execute("SELECT COUNT(*) FROM study_sessions")
        total_sessions = cursor.fetchone()[0]
        
        # Get active groups
        cursor.execute("""
            SELECT COUNT(DISTINCT g.group_id)
            FROM groups g
            JOIN study_activities sa ON g.group_id = sa.group_id
            JOIN study_sessions ss ON sa.study_activity_id = ss.study_activity_id
            WHERE ss.start_time >= date('now', '-30 days')
        """)
        active_groups = cursor.fetchone()[0]
        
        # Calculate streak
        cursor.execute("""
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
        """)
        current_streak = cursor.fetchone()[0]
        
        return {
            "total_vocabulary": total_vocabulary,
            "total_words_studied": total_words_studied,
            "mastered_words": mastered_words,
            "success_rate": float(success_rate),
            "total_sessions": total_sessions,
            "active_groups": active_groups,
            "current_streak": current_streak
        }
        
    except Exception as e:
        logger.error(f"Error calculating dashboard stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to calculate dashboard statistics"
        )
```
