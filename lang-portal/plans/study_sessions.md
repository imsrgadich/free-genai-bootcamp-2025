# Study Sessions API Implementation Plan

## 1. POST /api/study-sessions Implementation Steps

1. [ ] Add new route decorator and function:
   ```python
   @app.route('/api/study-sessions', methods=['POST'])
   @cross_origin()
   def create_study_session():
   ```

2. [ ] Inside function, extract data from request:
   ```python
   data = request.get_json()
   group_id = data.get('group_id')
   study_activity_id = data.get('study_activity_id')
   ```

3. [ ] Add validation:
   - [ ] Check if group_id and study_activity_id are provided
   - [ ] Query DB to verify group and activity exist
   - [ ] Return 400 error if validation fails

4. [ ] Insert new study session:
   - [ ] Use SQL INSERT INTO study_sessions
   - [ ] Include group_id, study_activity_id, created_at
   - [ ] Get the new session ID

5. [ ] Query session details:
   - [ ] Join with groups and study_activities tables
   - [ ] Get group_name and activity_name
   - [ ] Return full session object

## 2. POST /api/study-sessions/:id/review Implementation Steps

1. [ ] Add new route decorator and function:
   ```python
   @app.route('/api/study-sessions/<id>/review', methods=['POST'])
   @cross_origin() 
   def create_word_review(id):
   ```

2. [ ] Extract data from request:
   ```python
   data = request.get_json()
   word_id = data.get('word_id')
   correct = data.get('correct')
   ```

3. [ ] Add validation:
   - [ ] Check if word_id and correct are provided
   - [ ] Verify study session exists
   - [ ] Verify word exists
   - [ ] Return 400 error if validation fails

4. [ ] Insert word review:
   - [ ] Use SQL INSERT INTO word_review_items
   - [ ] Include word_id, study_session_id, correct, created_at
   - [ ] Get the new review ID

5. [ ] Return review details:
   - [ ] Format response with review ID and all fields
   - [ ] Include timestamps

## Testing Steps

1. [ ] Test POST /api/study-sessions:
   - [ ] Test with valid group/activity IDs
   - [ ] Test with invalid IDs
   - [ ] Verify response format matches spec
   - [ ] Check DB for new session

2. [ ] Test POST /api/study-sessions/:id/review:
   - [ ] Test with valid session/word
   - [ ] Test with invalid session/word
   - [ ] Test both correct=true and false
   - [ ] Verify review count increases
   - [ ] Check DB for new review items

## Error Cases to Handle

- [ ] Missing required fields
- [ ] Invalid group_id or study_activity_id
- [ ] Invalid study session ID
- [ ] Invalid word_id
- [ ] Database errors
- [ ] Invalid data types
