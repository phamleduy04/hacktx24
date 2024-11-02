import together
from sqlalchemy import create_engine, text
import requests

def connect():
    username = 'demo'
    password = 'demo'
    hostname = '2.tcp.ngrok.io:12180'
    # port = '1972'
    namespace = 'USER'
    CONNECTION_STRING = f"iris://{username}:{password}@{hostname}/{namespace}"
    engine = create_engine(CONNECTION_STRING)
    conn = engine.connect()
    client = together.Together()
    return client, conn

def reset_table(): 
     # Load 
    sql = f"""
    DROP TABLE data
    """
    result = conn.execute(text(sql))

    # Load 
    sql = f"""
        CREATE TABLE data (
        image_id INT PRIMARY KEY,
        image_link VARCHAR(2000),
        description VARCHAR(2000),
        description_vector VECTOR(DOUBLE, 768)
        )
        """
    result = conn.execute(text(sql))
    
def insert_data(image_id: int, image_link: str, description: str, description_vector: float):
    # Load 
    sql = f"""
    INSERT INTO data (image_id, image_link, description, description_vector)
    VALUES ({image_id}, '{image_link}', '{description}', {description_vector})
    """
    result = conn.execute(text(sql))


client, conn = connect()
