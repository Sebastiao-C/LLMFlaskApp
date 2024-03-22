from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import os
import numpy as np

from src.openai_azure_recommender import OpenAIRecommender
from src.recommender_system import RecommenderSystem, RandomRecommender
import numpy as np

Rec_sys = RecommenderSystem("data/jester_items.csv", "data/jester_ratings.csv")
rand_sys = RandomRecommender("data/jester_items.csv")
openai_sys = OpenAIRecommender("data/jester_items.csv")

import logging
logging.basicConfig(level=logging.DEBUG) 

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback_secret_key_for_development')

#app.secret_key = 'your_secret_key'

# This is a placeholder for user storage. Replace with database logic in a real app.
users = {'user1': {'password': 'password123'}}

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    if username not in users:
        return

    user = User()
    user.id = username
    return user

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash('Username already exists.')
        else:
            # Register logic here
            users[username] = {'password': password}
            flash('Successfully registered. Please log in.')
            return redirect(url_for('login'))
    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Assuming 'users' is your user storage
        user = users.get(username)
        if user and user['password'] == password:
            # Login logic here
            return redirect(url_for('protected'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/protected')
@login_required
def protected():
    return render_template('protected.html', username=session['_user_id'])


@app.route('/logout')
def logout():
    logout_user()
    return 'Logged out'

@app.route('/joke')
@login_required
def joke():
    # Assuming your existing joke generation logic here
    new_user = np.zeros(140)
    new_user[5] = 4
    new_user[20] = 3
    new_user[30] = -6
    new_user[40] = -9.9
    new_user[50] = -5
    joke = rand_sys.get_N_user_recommendations(new_user, 1)
    print(joke)
    return jsonify({'joke' : joke.iloc[0]})

@app.route('/submit_feedback', methods=['POST'])
@login_required
def submit_feedback():
    data = request.get_json()
    rating = data['rating']
    print(rating)
    # Process the rating here (e.g., store it in a database)
    return jsonify({'status': 'success'})

@app.route('/')
def welcome():
    return render_template('welcome.html')


if __name__ == '__main__':
    app.run(debug=True)
