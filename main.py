from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import numpy as np

from src.openai_azure_recommender import OpenAIRecommender
from src.recommender_system import RecommenderSystem, RandomRecommender
import numpy as np

from peewee import (
    Model, IntegerField, FloatField,
    TextField, IntegrityError, BooleanField
)
from playhouse.shortcuts import model_to_dict
from playhouse.db_url import connect

import pandas as pd

from random import random


Rec_sys = RecommenderSystem("data/jester_items.csv", "data/jester_ratings.csv")
rand_sys = RandomRecommender("data/jester_items.csv")
openai_sys = OpenAIRecommender("data/jester_items.csv")

import logging
logging.basicConfig(level=logging.DEBUG) 

DB = connect(os.environ.get('DATABASE_URL') or 'sqlite:///ratings.db')

class Rating(Model):
    userID = TextField()
    jokeID = IntegerField()
    rating = IntegerField()
    system = TextField()

    class Meta:
        database = DB


DB.create_tables([Rating], safe=True)



app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback_secret_key_for_development')

#app.config['SESSION_COOKIE_SECURE'] = True
#app.config['REMEMBER_COOKIE_SECURE'] = True 

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
            user_obj = User()
            user_obj.id = username
            login_user(user_obj)
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


@app.route('/show_ratings')
def show_ratings():
    ratings_df = get_ratings_dataframe()  # Assuming this function returns your DataFrame
    ratings_html = ratings_df.to_html(classes='data', index=False)  # Generate HTML
    return render_template('dataframe.html', ratings_html=ratings_html)

def get_ratings_dataframe():
    # Assuming Rating is your Peewee model for the ratings table
    query = Rating.select()
    # Convert the query to a list of dictionaries
    ratings_list = list(query.dicts()) 
    # Convert the list of dictionaries to a DataFrame
    ratings_df = pd.DataFrame(ratings_list)
    return ratings_df #jsonify(ratings_df.to_json(orient='records'))

# Example usage
#ratings_df = get_ratings_dataframe()
#print(ratings_df)


@app.route('/joke')
@login_required
def joke():
    new_user = np.zeros(140)  # Example user profile
    df = get_ratings_dataframe()
    userID = current_user.get_id()
    #print(df)
    #print(df)
    #print(df[df['userID'] == userID])
    if df.shape[0] == 0:
        joke = rand_sys.get_N_user_recommendations(new_user, 1)
        system = 'random'
    else:
        for row_ in df[df['userID'] == userID].iterrows():
            row = row_[1]
            new_user[row['jokeID']] = row['rating']

        if df[df['userID'] == userID].shape[0] < 5:
            joke = rand_sys.get_N_user_recommendations(new_user, 1)
            system = 'random'
        else:
            #print("HERE!")
            num = random()
            if num < 0.8:
                joke = Rec_sys.get_N_user_recommendations(new_user, 1)
                system = 'recommender'
            #elif num < 0.8:
            #    joke = openai_sys.get_N_user_recommendations(new_user, 1)   
            #    system = 'openai'
            else:
                joke = rand_sys.get_N_user_recommendations(new_user, 1)
                system = 'random'

    #print(joke)
    #print(joke.index[0])
    return jsonify({'joke': joke.iloc[0], 'jokeID': int(joke.index[0]), 'system' : system})

 


@app.route('/submit_feedback', methods=['POST'])
@login_required
def submit_feedback():
    data = request.get_json()
    rating = data['rating']
    jokeID = data['jokeID']
    system = data['system']
    userID = current_user.get_id()  # Assuming your User model or Flask-Login setup provides this

    new_rating = Rating(userID=userID, jokeID=jokeID, rating=rating, system=system)
    new_rating.save()
    return jsonify({'status': 'success', 'message': 'Feedback received'})

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/list-db-contents/')#, methods=['POST'])
def list_db_contents():
    return jsonify([
        model_to_dict(obs) for obs in Rating.select()
    ])



if __name__ == '__main__':
    app.run(debug=True)
