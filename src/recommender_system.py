import os

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
#%matplotlib inline

from numpy.linalg import norm
from scipy.sparse import csr_matrix, save_npz

from sklearn.metrics.pairwise import cosine_similarity

from IPython.display import Image

class RandomRecommender():
    def __init__(self, pathjokes : str) -> None:
        self.pathjokes = pathjokes
        self.jokes = pd.read_csv(pathjokes)
    
    def get_N_user_recommendations(self, new_user = None, N = 1):
        return self.jokes.iloc[np.random.randint(0, len(self.jokes), N)].jokeText

class RecommenderSystem():
    def __init__(self, pathjokes : str, pathratings : str) -> None:
        self.pathjokes = pathjokes
        self.pathratings = pathratings  
        self.jokes = pd.read_csv(self.pathjokes)
        self.ratings = pd.read_csv(self.pathratings)
        self.matrix = self.get_matrix()
        self.item_similarities = cosine_similarity(self.matrix.T, dense_output=False)


    def get_matrix(self):
        return csr_matrix(self.ratings.pivot(index='userId', columns='jokeId', values='rating')
                                .sort_index().fillna(0)) 
    
    def get_user_predictions(self, user_ratings):
        weighted_sum = np.dot(user_ratings, self.item_similarities.toarray())      

        R_boolean = user_ratings.copy() 
        R_boolean[R_boolean != 0] = 1 
        preds = np.divide(weighted_sum, np.dot(R_boolean, self.item_similarities.toarray())) 
        
        # Exclude previously rated items.
        preds[user_ratings.nonzero()] = 0
        
        return preds
    
    def get_N_user_recommendations(self, user_ratings, N):
        item_preds = self.get_user_predictions(user_ratings)
        return self.jokes.iloc[np.argpartition(item_preds, -N)[-N:]].jokeText

    


