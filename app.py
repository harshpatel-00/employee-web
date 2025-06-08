from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('employees.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        conn.close()
        
        if user:
            session['user'] = user['username']
            flash('Login successful!')
            return redirect(url_for('employees'))
        else:
            flash("Invalid credentials", 'danger')
    return render_template('login.html')
        

@app.route('/employees')
def employees():
    if 'user' not in session:
        flash('You need to log in first!', 'warning')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM employees").fetchall()
    conn.close()
    return render_template('view.html', employees=rows)

@app.route('/add', methods=['GET', 'POST'])
def add():
    
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']
        position = request.form['position']
        
        conn = get_db_connection()
        conn.execute("INSERT INTO employees (name, age, email, position) VALUES (?, ?, ?, ?)", (name, age, email, position))
        conn.commit()
        conn.close()
        flash('Employee added successfully!', 'success')
        return redirect(url_for('employees'))
    return render_template('add.html')


@app.route('/delete/<int:id>')
def delete(id):
    
    conn = get_db_connection()
    conn.execute("DELETE FROM employees WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Employee deleted.', 'danger')
    return redirect(url_for('employees'))


@app.route('/search', methods = ['GET', 'POST'])
def search():
    if 'user' not in session:
        flash('Please login to search employees.', 'warning')
        return redirect(url_for('login'))
    
    employees = []
    if request.method == 'POST':
        keyword = request.form['keyword']
        conn = get_db_connection()
        employees = conn.execute("SELECT * FROM employees WHERE name like ? OR position like ?", (f"%{keyword}%", f"%{keyword}%")).fetchall()
        conn.close()
    return render_template('search.html', employees = employees)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']
        position = request.form['position']
        conn.execute("UPDATE employees SET name = ?, age = ?, email = ?, position =? WHERE id = ?",(name, age, email, position, id))
        conn.commit()
        conn.close()
        flash('Employee updated.', 'info')
        return redirect(url_for('employees'))
    else:
        employee = conn.execute("SELECT * FROM employees WHERE id = ?", (id,)).fetchone()
        conn.close()
        return render_template('edit.html', employee = employee)
    
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))


def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS employees(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            email TEXT UNIQUE,
            position TEXT)
        ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()
    
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host = '0.0.0.0', port= port, debug=True)