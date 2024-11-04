from typing import Union
import requests
from pydantic import BaseModel
from fastapi import FastAPI
from datetime import datetime
from vector_store import search_by, start_server, insert_data

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
    response = requests.post("http://localhost:3000/chat", json={"prompt": "This is the relevant history: " + " ".join(["Person #" + str(i[0]) + ": " + i[1] for i in db_descriptions]) + "\nUse the relevant history to answer the following question and if you can't find exact matches, use the closest relevant people: " + question})
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
    
        return {
            "response": response,
            "img": results[0][2]
        }
    
    except Exception as e:
        return {
            "response": str(e),
            "img": ""
        }
        
class VectorResponse(BaseModel):
    id: int
    img: str
    description: str

@app.post("/vector")
def save_to_vector_db(vector_response: VectorResponse):
    
    try:
    
        # print(vector_response)
        
        # get time HH:MM AM/PM
        now = datetime.now()
        current_time = now.strftime("%H:%M %p")
        
        modified_desc = f"At {current_time}, {vector_response.description}"
        
        print(modified_desc)
        
        insert_data(conn, vector_response.id, vector_response.img, modified_desc)
        
    except Exception as e:
        return {
            "response": str(e)
        }
    
    return {
        "response": "Success"
    }