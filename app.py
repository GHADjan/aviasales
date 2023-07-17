
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Конфигурация базы данных PostgreSQL
DB_HOST = '127.0.0.1'
DB_NAME = 'aviasalesdb'
DB_USER = 'postgres'
DB_PASSWORD = 'admin'


# Установка соединения с базой данных PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tickets')
    flights = cursor.fetchall()
    cursor.close()
    conn.close()

    if 'username' in session:
        return render_template('index.html', username=session['username'], flights=flights)
    else:
        return render_template('index.html', flights=flights)


# Форма поиска билетов
@app.route('/search', methods=['POST'])
def search():
    origin = request.form['origin']
    destination = request.form['destination']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tickets WHERE origin = %s AND destination = %s', (origin, destination))
    flights = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('search_results.html', origin=origin, destination=destination, flights=flights)


# Форма входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['user_id'] = user[0]

            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
    else:
        return render_template('login.html')


# Форма регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
        conn.commit()
        cursor.close()
        conn.close()

        session['username'] = username
        return redirect(url_for('index'))
    else:
        return render_template('register.html')


# Выход
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


# Форма добавления билета
@app.route('/add_ticket', methods=['GET', 'POST'])
def add_ticket():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        origin = request.form['origin']
        destination = request.form['destination']
        date = request.form['date']
        price = request.form['price']
        user_id = session['user_id']

        # Преобразование строки даты в объект datetime

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO tickets (user_id, origin, destination, date, price) VALUES (%s, %s, %s, %s, %s)',
                (user_id, origin, destination, date, price))
            conn.commit()
        except Exception as e:
            # Обработка ошибки
            print(f"Error inserting ticket: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('index'))
    else:
        return render_template('add_ticket.html')


@app.route('/api/flights', methods=['GET'])
def get_flights():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tickets')
    flights = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(flights)


if __name__ == '__main__':
    app.run(debug=True)
