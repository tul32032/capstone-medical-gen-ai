--QUERIES TO SAVE DATA
--For $ signs, replace with correlating information in the INSERT INTO statement above
--or whatever the $ is equal to

--Saves a new user in the database
INSERT INTO users (email_address, password_hash)
VALUES ($1, $2)
RETURNING user_id;

--Saves a new session in the database
INSERT INTO sessions (user_id)
VALUES ($1)
RETURNING session_id;

--Saves a new question in the databse
INSERT INTO questions (user_id, session_id, question, answer, citations)
VALUES ($1, $2, $3, $4, $5)
RETURNING message_id;

--QUERIES TO CALL DATA

--Pulls a past session
SELECT question, answer, citations, time_stamp
FROM questions
WHERE session_id = $1
ORDER BY time_stamp;

--Pulls a user's complete chat history
SELECT question, answer, citations
FROM questions
WHERE user_id = $1
ORDER BY time_stamp;