from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
import json

from chat import EnvironmentalExpert
from models import db, User, ChatMessage
from forms import LoginForm, RegistrationForm

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'dsxwbkwbcekcjkjnkne2'  # Change this!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
CORS(app)
db.init_app(app)
bcrypt = Bcrypt(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access the chat.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize the environmental expert
expert = EnvironmentalExpert()

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('chat'))
        flash('Invalid email or password')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, 
                   email=form.email.data, 
                   password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

# Main Routes
# @app.route('/')
# def home():
#     if current_user.is_authenticated:
#         return redirect(url_for('chat'))
#     return redirect(url_for('login'))

@app.route('/')
def environment():
    return render_template('environment.html')

@app.route('/dashboard')
def dashboard():
    
    return render_template('dashboard.html')

@app.route('/chat')
@login_required
def chat():
    # Load user's chat history
    messages = ChatMessage.query.filter_by(user_id=current_user.id)\
                              .order_by(ChatMessage.timestamp.asc()).all()
    return render_template('chat.html', messages=messages)

@app.route('/api/chat', methods=['POST'])
@login_required
def chat_api():
    try:
        data = request.get_json()
        user_message = data.get('message', '')

        if not user_message.strip():
            return jsonify({'error': 'Empty message'}), 400

        # Get response from the EnvironmentalExpert
        bot_response = expert.get_response(user_message)
        sources = expert.get_last_sources()

        # Save to database
        chat_message = ChatMessage(
            user_id=current_user.id,
            user_message=user_message,
            bot_response=bot_response,
            sources=json.dumps(sources) if sources else json.dumps(['IPCC', 'NASA', 'NOAA', 'UNEP'])
        )
        db.session.add(chat_message)
        db.session.commit()

        response = {
            'response': bot_response,
            'sources': sources if sources else ['IPCC', 'NASA', 'NOAA', 'UNEP']
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# # Database initialization
# @app.before_first_request
# def create_tables():
#     db.create_all()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)