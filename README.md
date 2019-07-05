# Question-Answer-App
- A Q&amp;A app that consists of three roles which are admin, expert, and user. 
- Users post their questions and specify which expert to answer it. 
- Admin has the authority to determine which user could be the expert for answering the question.
- This app doesn't use Flask-SQLALCHEMY extension. 

## Installation
1. Create a virtual environment and install the dependencies.
```
pip install -r requirements.txt
```
2. Run the following code in your terminal and input your database's name in <database's name>.
```
sqlite3 <database's name> < schema.sql
```
3. Open db.py and replace question.db to your database's name in connect_db function.
```
sql = sqlite3.connect(os.path.join(os.path.dirname(__name__), os.path.abspath('question.db')))
```
4. Run app.py
5. Once the app is running, create a new user with name = 'admin' for administration.
6. Run the following code and SQL:
```
sqlite3
UPDATE users SET admin = 1 WHERE name = 'admin'
```
7. Login as admin and now you have the authority to decide which user can becomes an expert to answer the questions! 
