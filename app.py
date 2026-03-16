from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import get_db, init_db
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'bookclub_secret_key_2026'

# Initialize database on startup
with app.app_context():
    init_db()

# ---------- HOME ----------
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')

# ---------- REGISTER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        try:
            conn = get_db()
            conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                         (username, email, hashed_password))
            conn.commit()
            conn.close()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Email or username already exists.', 'error')

    return render_template('register.html')

# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

# ---------- BOOKS ----------
@app.route('/books')
def books():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('books.html', username=session['username'])

# ---------- PROFILE ----------
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('profile.html', user=user)

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------- CHANGE PASSWORD ----------
@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        current = request.form['current_password']
        new = request.form['new_password']
        conn = get_db()
        try:
            user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
            if user and check_password_hash(user['password'], current):
                conn.execute('UPDATE users SET password = ? WHERE id = ?',
                            (generate_password_hash(new), session['user_id']))
                conn.commit()
                flash('Password updated successfully.', 'success')
                return redirect(url_for('profile'))
            else:
                flash('Current password is incorrect.', 'error')
        finally:
            conn.close()
    return render_template('change_password.html')

# ---------- EDIT NAME ----------
@app.route('/edit-name', methods=['GET', 'POST'])
def edit_name():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_name = request.form['username']
        conn = get_db()
        try:
            conn.execute('UPDATE users SET username = ? WHERE id = ?',
                        (new_name, session['user_id']))
            conn.commit()
            session['username'] = new_name
            flash('Name updated successfully.', 'success')
            return redirect(url_for('profile'))
        finally:
            conn.close()
    return render_template('edit_name.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)