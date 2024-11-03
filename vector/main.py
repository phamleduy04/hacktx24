from typing import Union
import requests

from pydantic import BaseModel

from fastapi import FastAPI

from vector_store import search_by, start_server

from fastapi.middleware.cors import CORSMiddleware

conn = start_server()

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_keywords(question: str) -> str:
    # make a post request to localhost:8000/chat with the body
    response = requests.post("http://localhost:3000/chat", json={"prompt": "Give me at most 10 keywords from the following statement. If it is a questions, avoid trying to find the answer and give the keywords.\n" + question})
    # return the response
    return response.text

def get_friendly_response(db_descriptions: list, question: str) -> str:
    # make a post request to localhost:8000/chat
    response = requests.post("http://localhost:3000/chat", json={"prompt": "This is the relevant history: " + " ".join(["Person #" + str(i[0]) + ": " + i[1] for i in db_descriptions]) + "\nUse the relevant history to answer the following question: " + question})
    # return the response
    return response.text

class QuestionResponse(BaseModel):
    question: str

# post a question to the model
@app.post("/question")
def post_question(question_response: QuestionResponse):
    
    try:
    
        question = question_response.question
        
        print(question)
        
        # call the model to get a query to send to the database
        # keywords = get_keywords(question)
        
        # make call to the vector db to get relevant vectors
        results = search_by(conn, question)
        
        # call the model to get a friendly response
        response = get_friendly_response(results, question)
    
        return response
    
    except Exception as e:
        return str(e)
