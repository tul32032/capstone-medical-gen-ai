Setting Up the Local PostgreSQL Database
Install PostgreSQL
Download the latest PostgreSQL version: https://www.postgresql.org/download/
Run the installer and keep clicking Next.
You will be prompted to create a password for the postgres user. Choose something easy to remember, as you’ll use it later.
Make sure all four default applications are selected for installation.
* pgAdmin will be one of the applications
After installation, when prompted to open Stack Builder, uncheck it and click Finish.
Open pgAdmin and Connect to the Server
Launch pgAdmin.
On the left sidebar, find the PSQL Tool Workspace.
A prompt will appear: “Let’s Connect to the Server!”
* Select Existing Server (optional). 
It should show the server you created during installation. Select it.
Enter the password you created during installation.
You should now see a terminal with a prompt similar to: postgres=#
Create the Database
On the command line to the prompt, run:
CREATE DATABASE med_db;


You should get the following back:
CREATE DATABASE
Set Up Tables (Schema)
Run the following commands from the terminal or copy from your local-schema.sql file:
CREATE TABLE users(
   user_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   email_address TEXT UNIQUE,
   password_hash TEXT
);


CREATE TABLE sessions(
   session_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
   time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE questions(
   message_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
   session_id INT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
   time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   question TEXT,
   answer TEXT,
   citations TEXT
);
You should see a CREATE TABLE message as a result.
Verify Database Creation
Run:
SELECT * FROM users;
SELECT * FROM sessions;
SELECT * FROM questions;
* You should see empty tables, confirming that the database and tables are saved.
* Your local database is now persistent and ready to use.
Connect the Local Database to Python Backend
Your Python code requires a driver to communicate with PostgreSQL.
* Recommended: psycopg2
Use the following connection information for local development:
Host: localhost
Port: 5432
Database: med_db
User: postgres
Password: your_password
Create a .env file in your project folder and add:
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/med_db
In your code, you can use psycopg2 functions to read the URL from the .env, manually read it but will still need to use psycopg2 later, or whatever works best for you.
Transition to Google Cloud for Deployment
When we are ready to deploy, only the .env value will need to be changed. Like the following, which is also in the Database file as .env.ex:
DATABASE_URL=postgresql://user:password@CLOUD_IP:5432/med_db
* The database structure and queries remain the same.
* The transition from local to cloud will only require recreating the database by creating the database and running the schema file.