Setting Up the Local PostgreSQL Database


Install PostgreSQL
Download the latest PostgreSQL version: https://www.postgresql.org/download/
Run the installer and keep clicking Next.
You will be prompted to create a password for the postgres user. Choose something easy to remember, as you’ll use it later.
Make sure all four default applications are selected for installation.
- pgAdmin will be one of the applications
After installation, when prompted to open Stack Builder, uncheck it and click Finish.
Open pgAdmin and Connect to the Server
Launch pgAdmin.
On the left sidebar, find the PSQL Tool Workspace.
A prompt will appear: “Let’s Connect to the Server!”
- Select Existing Server (optional). 
It should show the server you created during installation. Select it.
Enter the password you created during installation.
You should now see a terminal with a prompt similar to: postgres=#


Create a .env file in your project folder that will be temporary for our local database and will be changed later
Insert:
DATABASE_NAME=med_db
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=your_password
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432


Create the Database in PostgreSQL on the command line
Run:
CREATE DATABASE med_db;

On the command line to the prompt change directory to application folder with manage.py
Run:
python manage.py makemigrations
python manage.py migrate

You should get the following back:
Applying contenttypes.0001_initial... OK
Applying auth.0001_initial... OK
Applying authentication.0001_initial... OK
Applying core.0001_initial... OK
- Django created all the tables
- Your local database is now persistent and ready to use.


Run the application
python manage.py runserver
- The application is now connected to the local PostgreSQ, and saves and rertieves data automatically.

Transition to Google Cloud for Deployment
When we are ready to deploy, only the .env value will need to be changed. Like the following, which is also in the Database file as .env.ex:
DATABASE_NAME=med_db
DATABASE_USERNAME=your_cloud_user
DATABASE_PASSWORD=your_cloud_password
DATABASE_HOST=CLOUD_IP
DATABASE_PORT=5432

- The database structure and queries remain the same.
- The transition from local to cloud will only require recreating the database by creating the database and running the schema file.