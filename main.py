from flask import Flask, jsonify
import os

from src.openai_azure_recommender import OpenAIRecommender
from src.recommender_system import RecommenderSystem, RandomRecommender
import numpy as np

app = Flask(__name__)

Rec_sys = RecommenderSystem("data/jester_items.csv", "data/jester_ratings.csv")
rand_sys = RandomRecommender("data/jester_items.csv")
openai_sys = OpenAIRecommender("data/jester_items.csv")


@app.route('/')
def index():
    new_user = np.zeros(140)
    new_user[5] = 4
    new_user[20] = 3
    new_user[30] = -6
    new_user[40] = -9.9
    new_user[50] = -5
    joke = rand_sys.get_N_user_recommendations(new_user, 1)
    return jsonify({"Choo Choo": f"{str(joke)}"})


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
