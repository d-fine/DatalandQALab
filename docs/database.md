# Guide to using a database along with this program

## Connect your local postgres
In order to connect your local PostgreSQL database do the following steps:
1. Download and install PostgreSQL on your local machine. During this proccess you hvae to set a username and password, please remember these credentials.
2. Download PGAdmin4 and inside it, create a database named "dataland_qa_lab"
3. In the .env file of the dataland_qa_lab add your database connection string like this:

DATABASE_CONNECTION_STRING=postgresql+pg8000://{username}.{password}@localhost:5432/dataland_qa_lab

Use your postgres credentials in the connection string.

## Add a new table
1. Create a class in src/dataland_qa_lab/database/database_tables
2. Call the method create_tables from src/dataland_qa_lab/database/database_engine

## Perform CRUD-Actions
To perform basic CRUD-Actions to the database use the generic methods:
 add_entity(), 
 get_entity(), 
 update_entity(), 
 delete_entity() 
from src/dataland_qa_lab/database/database_engine


