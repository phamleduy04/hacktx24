import together
from sqlalchemy import create_engine, text
import requests

from sentence_transformers import SentenceTransformer

import base64

encoded_string = ""

# read img from dog.jpg and convert to base64
# with open("dog.jpg", "rb") as image_file:
#     encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

# Load a pre-trained sentence transformer model. This model's output vectors are of size 384
model = SentenceTransformer('all-MiniLM-L6-v2')
client = None

def connect():
    username = 'demo'
    password = 'demo'
    hostname = '2.tcp.ngrok.io:12180'
    # port = '1972'
    namespace = 'USER'
    CONNECTION_STRING = f"iris://{username}:{password}@{hostname}/{namespace}"
    engine = create_engine(CONNECTION_STRING)
    conn = engine.connect()
    return None, conn


def reset_table(conn):
    # Load
    try:
        sql = """
        DROP TABLE data
        """
        result = conn.execute(text(sql))
        # print(result)
    except Exception as e:
        print("Table does not exist")

    # Load
    sql = """
        CREATE TABLE data (
        image_id INT PRIMARY KEY,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        base_64_image LONGTEXT,
        description VARCHAR(2000),
        description_vector VECTOR(DOUBLE, 384)
        )
        """
    result = conn.execute(text(sql))

def insert_data(conn, image_id: int, base_64_image: str, description: str, vector=None):

    if vector == None:
        vector = model.encode(description, normalize_embeddings=True).tolist()

    sql = text("""
        INSERT INTO data
        (image_id, base_64_image, description, description_vector)
        VALUES (:image_id, :base_64_image, :description, TO_VECTOR(:description_vector))
        """)

    result = conn.execute(sql, {
        'image_id': image_id,
        'base_64_image': base_64_image,
        'description': description,
        'description_vector': str(vector),
    })


def read_all_data(conn):
    # get all data
    sql = """
    SELECT * FROM data
    """
    print("READING")
    result = conn.execute(text(sql))
    print(result.fetchall())


def search_by(conn, description):
    # search by description
    # This is our search phrase

    # Convert search phrase into a vector
    searchVector = model.encode(
        description, normalize_embeddings=True).tolist()
    
    limit = 3

    # Define the SQL query with placeholders for the vector and limit
    sql = f"""
    SELECT TOP {limit} image_id, description, base_64_image
    FROM data
    ORDER BY VECTOR_DOT_PRODUCT(description_vector, TO_VECTOR(:searchVector)) DESC
"""

    # Execute the query with the number of results and search vector as parameters
    searchQuery = conn.execute(text(sql), {
        'searchVector': str(searchVector),
    })

    # Fetch all results
    results = searchQuery.fetchall()
    for row in results:
        print(row)
        
    return results


def start_server():
    print("Starting server")
    
    client, conn = connect()

    reset_table(conn)
    #insert_data(1, 'https://www.google.com', 'A picture of a cat')
    #insert_data(2, 'https://www.google.com', 'A picture of a dog')
    #insert_data(3, 'https://www.google.com', 'A picture of a tiger')
    insert_data(conn, 4, encoded_string, 'At 3:45 PM, The person is wearing a black short sleeve shirt and gray trousers.')
    insert_data(conn, 5, encoded_string, 'At 3:45 PM, The person is wearing a green long sleeve shirt and black pants.')
    insert_data(conn, 6, encoded_string, 'At 4:20 PM, The person is wearing a white short sleeve shirt and pink trousers.')
    insert_data(conn, 7, encoded_string, 'At 10:15 PM, The person is wearing a blue long sleeve shirt and cyan pants.')
    insert_data(conn, 8, encoded_string, 'At 1:30 PM, The person is wearing a violet short sleeve shirt and yellow trousers.')
    insert_data(conn, 9, encoded_string, 'At 6:00 PM, The person is wearing a orange long sleeve shirt and indigo pants.')
    insert_data(conn, 10, encoded_string, 'At 9:15 AM, The person is wearing a red short sleeve shirt and white trousers.')


    # read_all_data()

    search_by(conn, '3:45 PM')
    
    return conn
