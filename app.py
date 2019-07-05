from flask import Flask, render_template, g, request, session, redirect, url_for
from db import get_db
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
# os.urandom(24)
app.config['SECRET_KEY'] = b'\x13\x9dU\xffJ\xa3X\x9a.\x8eA)/\xc2\x83\x81V\x1b\x10\x98\x1b\xe1\xab\x92'


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def get_current_user():
    user_result = None
    if 'user' in session:
        user = session['user']

        db = get_db()
        user_cursor = db.execute('SELECT id, name, password, expert, admin FROM users WHERE name = ?', [user])
        user_result = user_cursor.fetchone()

    return user_result


@app.route('/')
def index():
    user = get_current_user()
    db = get_db()

    question_cursor = db.execute('''SELECT questions.id AS question_id, questions.question_text AS question_text, 
                                    askers.name AS asker_name, experts.name AS expert_name
                                    FROM questions 
                                    JOIN users AS askers ON askers.id = questions.asked_by_id 
                                    JOIN users AS experts ON experts.id = questions.expert_id 
                                    WHERE questions.answer_text is NOT NULL''')
    question_results = question_cursor.fetchall()

    return render_template('home.html', user=user, questions=question_results)


@app.route('/register', methods=['POST', 'GET'])
def register():
    user = get_current_user()
    if request.method == 'POST':
        db = get_db()
        existing_user_cursor = db.execute('SELECT id FROM users WHERE name = ?', [request.form['name']])
        existing_user = existing_user_cursor.fetchone()

        if existing_user:
            return render_template('register.html', user=user, error='User already exists!')

        hashed_password = generate_password_hash(request.form['password'], method='sha256')
        db.execute('INSERT INTO users (name, password, expert, admin) VALUES (?, ?, ?, ?)',
                   [request.form['name'], hashed_password, '0', '0'])
        db.commit()
        session['user'] = request.form['name']
        return redirect(url_for('index'))
    return render_template('register.html', user=user)


@app.route('/login', methods=['POST', 'GET'])
def login():
    user = get_current_user()
    username_error = None
    password_error = None

    if request.method == 'POST':
        db = get_db()
        name = request.form['name']
        password = request.form['password']

        user_cursor = db.execute('SELECT id, name, password FROM users WHERE name = ?', [name])
        user_result = user_cursor.fetchone()

        if user_result:
            if check_password_hash(user_result['password'], password):
                session['user'] = user_result['name']
                return redirect(url_for('index'))
            else:
                password_error = 'The password is incorrect.'
        else:
            username_error = 'The username is incorrect'

    return render_template('login.html', user=user, username_error=username_error, password_error=password_error)


@app.route('/question/<question_id>')
def question(question_id):
    user = get_current_user()
    db = get_db()

    question_cursor = db.execute('''SELECT questions.question_text AS question_text, 
                                    questions.answer_text AS answer_text,
                                    askers.name AS asker_name, experts.name AS expert_name
                                    FROM questions 
                                    JOIN users AS askers ON askers.id = questions.asked_by_id 
                                    JOIN users AS experts ON experts.id = questions.expert_id 
                                    WHERE questions.id = ?''', [question_id])
    question_results = question_cursor.fetchone()

    return render_template('question.html', user=user, question=question_results)


@app.route('/answer/<question_id>', methods=['POST', 'GET'])
def answer(question_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    if user['expert'] == 0:
        return redirect(url_for('index'))

    db = get_db()

    if request.method == 'POST':
        db.execute('UPDATE questions SET answer_text = ? WHERE id = ?', [request.form['answer'], question_id])
        db.commit()
        return redirect(url_for('unanswered'))

    question_cursor = db.execute('SELECT id, question_text FROM questions WHERE id = ?', [question_id])
    question_results = question_cursor.fetchone()

    return render_template('answer.html', user=user, question=question_results)


@app.route('/ask', methods=['POST', 'GET'])
def ask():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    db = get_db()

    if request.method == 'POST':
        db.execute('INSERT INTO questions (question_text, asked_by_id, expert_id) VALUES (?, ?, ?)',
                   [request.form['question'], user['id'], request.form['id']])
        db.commit()

        return redirect(url_for('index'))

    expert_cursor = db.execute('SELECT id, name FROM users WHERE expert = 1')
    expert_results = expert_cursor.fetchall()
    return render_template('ask.html', user=user, experts=expert_results)


@app.route('/unanswered')
def unanswered():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    if user['expert'] == 0:
        return redirect(url_for('index'))

    db = get_db()

    question_cursor = db.execute('''SELECT questions.id, questions.question_text, users.name
                                    FROM questions 
                                    JOIN users ON users.id = questions.asked_by_id
                                    WHERE questions.answer_text is NULL 
                                    AND questions.expert_id = ?''', [user['id']])
    question_results = question_cursor.fetchall()

    return render_template('unanswered.html', user=user, questions=question_results)


@app.route('/users')
def users():
    user = get_current_user()

    if not user:
        return redirect(url_for('login'))

    if user['admin'] == 0:
        return redirect(url_for('index'))

    db = get_db()
    user_cursor = db.execute('SELECT id, name, expert, admin FROM users')
    user_results = user_cursor.fetchall()
    return render_template('users.html', user=user, users=user_results)


@app.route('/promote/<user_id>')
def promote(user_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    if user['admin'] == 0:
        return redirect(url_for('index'))

    db = get_db()
    db.execute('UPDATE users SET expert = 1 WHERE id = ?', [user_id])
    db.commit()
    return redirect(url_for('users'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=5002)
