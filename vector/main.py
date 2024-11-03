from typing import Union
import requests

from fastapi import FastAPI

from vector_store import search_by

app = FastAPI()

def get_keywords(question: str) -> str:
    # make a post request to localhost:8000/chat
    response = requests.post("http://localhost:3000/chat", data={"question": question})
    # return the response
    return response.text

def get_friendly_response(db_descriptions) -> str:
    # make a post request to localhost:8000/chat
    response = requests.post("http://localhost:3000/chat", data={"db_descriptions": db_descriptions})
    # return the response
    return response.text

# post a question to the model
@app.post("/question")
def post_question(question: str):
    # call the model to get a query to send to the database
    keywords = get_keywords(question)
    
    # make call to the vector db to get relevant vectors
    results = search_by(keywords)
    
    # call the model to get a friendly response
    response = get_friendly_response(results)
    
    return response
