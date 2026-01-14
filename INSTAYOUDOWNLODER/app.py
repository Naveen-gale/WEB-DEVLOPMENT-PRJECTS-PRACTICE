from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pytube import YouTube
import os

app = Flask(__name__)
app.secret_key = 'secretkey123'

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# DB + Login
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Create DB
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('register'))
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Registered! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email and password are required!', 'error')
            return redirect(url_for('login'))

        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            flash('Logged in successfully', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    video_info = None
    if request.method == 'POST':
        url = request.form['video_url']
        try:
            yt = YouTube(url)
            video_info = {
                "title": yt.title,
                "thumbnail": yt.thumbnail_url,
                "url": url,
                "streams": yt.streams.filter(progressive=True, file_extension='mp4')
            }
        except Exception as e:
            flash("Invalid YouTube URL!", "error")
    return render_template("dashboard.html", video_info=video_info)

@app.route('/download_video', methods=['POST'])
@login_required
def download_video():
    url = request.form['video_url']
    quality = request.form['quality']
    try:
        yt = YouTube(url)
        stream = yt.streams.get_by_itag(quality)
        stream.download(output_path="downloads")
        flash('✅ Download complete!', 'success')
    except Exception as e:
     print("Error fetching video:", e)  # Debug
     flash("❌ Invalid YouTube URL or error fetching video!", "error")
    return redirect(url_for('dashboard'))


    return redirect(url_for('dashboard'))





   

if __name__ == '__main__':
    app.run(debug=True)
