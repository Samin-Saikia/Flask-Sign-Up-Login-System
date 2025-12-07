from flask import Flask, render_template, request, redirect, url_for, flash
from flask import render_template_string
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import or_
from flask import session, render_template_string
from flask import g  # add if not already imported

app = Flask(__name__)
app.secret_key = "secret"
# Use your sqlite path — keep three slashes for absolute Windows path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/CodeVerce/sign up and login system/login.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Login(db.Model):
    __tablename__ = 'logins'
    sno = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, username, password, mail):
        self.username = username
        self.password = password
        self.mail = mail

with app.app_context():
    db.create_all()
    print("Database tables created or already exist at:", app.config['SQLALCHEMY_DATABASE_URI'])

@app.route('/', methods=['GET', 'POST'])


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        mail = request.form.get('mail', '').strip().lower()

        # Basic validation
        if not username or not password or not mail:
            # show alert then redirect back
            return render_template_string('''
                <script>alert("Please fill all fields."); window.location = "{{ url_for('home') }}";</script>
            ''')

        # Check for existing username
        existing_user = Login.query.filter_by(username=username).first()
        if existing_user:
            return render_template_string('''
                <script>alert("This username already exists. Please choose a different username."); window.location = "{{ url_for('home') }}";</script>
            ''')

        # Check for existing email
        existing_mail = Login.query.filter_by(mail=mail).first()
        if existing_mail:
            return render_template_string('''
                <script>alert("This email is already registered. Use another email or log in."); window.location = "{{ url_for('home') }}";</script>
            ''')

        # Check for existing password (optional)
        existing_password = Login.query.filter_by(password=password).first()
        if existing_password:
            return render_template_string('''
                <script>alert("This password is already in use. Please choose a different password."); window.location = "{{ url_for('home') }}";</script>
            ''')

        entry = Login(username=username, password=password, mail=mail)
        try:
            db.session.add(entry)
            db.session.commit()
            app.logger.info('DATA ADDED: %s', username)
            flash("Signup successful!", "success")
            return redirect(url_for('signed'))
        except Exception as e:
            db.session.rollback()
            app.logger.exception("Failed to add entry")
            flash(f"An error occurred: {e}", "error")
            return redirect(url_for('home'))

    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Accept either "identifier" (preferred) or fallback to "username"
        identifier = (request.form.get('identifier') or request.form.get('username') or '').strip()
        password = request.form.get('password', '').strip()

        # Basic validation (server-side)
        if not identifier or not password:
            return render_template_string('''
                <script>
                  alert("Please fill all fields.");
                  window.location = "{{ url_for('login') }}";
                </script>
            ''')

        # Try to find user by username OR email (case-insensitive for email)
        user = Login.query.filter(
            or_(Login.username == identifier, Login.mail == identifier.lower())
        ).first()

        # Case: no user found (username/email not registered)
        if not user:
            return render_template_string('''
                <script>
                  alert("No username or email like this exists. Please sign up first.");
                  window.location = "{{ url_for('login') }}";
                </script>
            ''')

        # Case: password mismatch
        # NOTE: you are storing plaintext passwords now — for production use hashing.
        if user.password != password:
            return render_template_string('''
                <script>
                  alert("Password doesn't match. Try again.");
                  window.location = "{{ url_for('login') }}";
                </script>
            ''')

        # Success: set session and redirect to protected page (/logd)
        session['user_id'] = user.sno
        flash("Login successful!", "success")
        return redirect(url_for('logd'))

    # GET -> render login template
    return render_template('login.html')


@app.route('/signed')
def signed():
    return render_template('signed.html')

@app.route('/logd')
def logd():
    return render_template('logd.html')
if __name__ == '__main__':
    # If you're testing from another device, set host='0.0.0.0', otherwise leave default
    app.run(debug=True)
