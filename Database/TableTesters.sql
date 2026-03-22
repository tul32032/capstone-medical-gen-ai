--TABLES TESTER & CLEANUP AFTER
INSERT INTO users (email_address, password_hash)
VALUES ('test_users', 'hashedpassword123')
RETURNING user_id;

INSERT INTO sessions (user_id)
VALUES (1)
RETURNING session_id;

INSERT INTO questions(user_id, session_id, question, answer, citations)
VALUES (1, 1, 'What is diabetes?', 'Diabetes is ...', 'source with citations')
RETURNING message_id;

--Cleanup
DELETE FROM questions;
DELETE FROM sessions;
DELETE FROM users;