import os

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
#%matplotlib inline

from numpy.linalg import norm
from scipy.sparse import csr_matrix, save_npz

from sklearn.metrics.pairwise import cosine_similarity

#from IPython.display import Image

from openai import AzureOpenAI # Diferente

import json


class OpenAIRecommender():
    def __init__(self, pathjokes : str, temperature = 1, max_tokens = 64) -> None:
        self.pathjokes = pathjokes
        self.jokes = pd.read_csv(self.pathjokes)

        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def get_best_and_worst_rated(self, user_ratings):
        return (self.jokes.iloc[np.argmax(user_ratings)].jokeText, self.jokes.iloc[np.argmin(user_ratings)].jokeText)
    
    def get_N_user_recommendations(self, user_ratings, N):
        best, worst = self.get_best_and_worst_rated(user_ratings)
        jokes = []
        for _ in range(N):
            prompt = f"Here is a user's favorite joke:\n\n{best}\n\nAnd this is their least favorite joke:\n\n{worst}\n\nGive me your best joke with these user's preferences in mind."

            api_endpoint = "https://scaoai1.openai.azure.com/"
            api_key = "43866e96daa54d5cb0f5dce46dc3223d"
            api_version = "2024-02-15-preview"
            api_deployment_name = "sc-gpt-35-turbo" #"sc-gpt-4"

            client = AzureOpenAI(api_key=api_key, api_version=api_version, azure_endpoint=api_endpoint) # Diferente

            response = client.chat.completions.create(
            model=api_deployment_name, # Diferente
            messages=[
                {
                "role": "system",
                "content": "You will be provided with a user's favorite and least favorites jokes, and your task is to generate the best joke according to the user's preferences. You should only generate a joke and no additional text."
                },
                {
                "role": "user",
                "content": prompt#"My name is Jane. What is yours?"
                }
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=1
            )
            jokes.append(json.loads(response.model_dump_json())['choices'][0]['message']['content'])
        return jokes

        


