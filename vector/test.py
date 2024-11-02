import together
from sqlalchemy import create_engine, text
import requests

from sentence_transformers import SentenceTransformer

# Load a pre-trained sentence transformer model. This model's output vectors are of size 384
model = SentenceTransformer('all-MiniLM-L6-v2')


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


def reset_table():
    # Load
    try:
        sql = """
        DROP TABLE data
        """
        result = conn.execute(text(sql))
        print(result)
    except Exception as e:
        print("Table does not exist")

    # Load
    sql = """
        CREATE TABLE data (
        image_id INT PRIMARY KEY,
        image_link VARCHAR(2000),
        description VARCHAR(2000),
        description_vector VECTOR(DOUBLE, 384)
        )
        """
    result = conn.execute(text(sql))
    print(result)


def insert_data(image_id: int, image_link: str, description: str, vector=None):

    # """sql = text("""
    #     INSERT INTO pictures
    #     (image_id, image_link, user_id, description, description_vector)
    #     VALUES (:image_id, :image_link, :user_id, :description, TO_VECTOR(:description_vector))
    # """)

    # conn.execute(sql, {
    #     'image_id': row['image_id'],
    #     'image_link': row['image_link'],  # Provide actual image data here
    #     'user_id': row['user'],
    #     'description': row['description'],
    #     'description_vector': str(row['description_vector']),
    # })

    # outputs = client.embeddings.create(input=df['description'].tolist(), model='togethercomputer/m2-bert-80M-2k-retrieval')
    # df['description_vector'] = [outputs.data[i].embedding for i in range(len(df['description']))]

    if vector == None:

        # embeds = client.embeddings.create(input=description, model='togethercomputer/m2-bert-80M-2k-retrieval')
        # vector = embeds.data[0].embedding
        vector = model.encode(description, normalize_embeddings=True).tolist()

    # print("EMBEDS", vector)
    # print("EMBEDS2", str(vector))

    sql = text("""
        INSERT INTO data
        (image_id, image_link, description, description_vector)
        VALUES (:image_id, :image_link, :description, TO_VECTOR(:description_vector))
        """)

    result = conn.execute(sql, {
        'image_id': image_id,
        'image_link': image_link,
        'description': description,
        'description_vector': str(vector),
    })

    print(result)


def read_all_data():
    # get all data
    sql = """
    SELECT * FROM data
    """
    print("READING")
    result = conn.execute(text(sql))
    print(result.fetchall())


def search_by(description):
    # search by description
    # This is our search phrase

    # Convert search phrase into a vector
    searchVector = model.encode(
        description, normalize_embeddings=True).tolist()
    
    limit = 3

    # Define the SQL query with placeholders for the vector and limit
    sql = f"""
    SELECT TOP {limit} image_id, image_link, description
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


client, conn = connect()
reset_table()
insert_data(1, 'https://www.google.com', 'A picture of a cat')
insert_data(2, 'https://www.google.com', 'A picture of a dog')
insert_data(3, 'https://www.google.com', 'A picture of a tiger')
read_all_data()

search_by('labrador')
