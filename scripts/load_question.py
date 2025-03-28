import json
import os
import psycopg2 as pg
from config import config

def connect_db():
    """
    Establish a connection to the PostgreSQL database.
    """
    conn = pg.connect(**config)
    return conn

def load_questions_from_json(topic):
    """
    Loads questions from the JSON file for the given topic.

    Args:
        topic (str): The topic name (e.g., 'geography', 'history', etc.)
    """
    file_path = f"data/{topic}.json"
    with open(file_path, 'r') as file:
        return json.load(file)

def insert_questions_from_json(topic):
    """
    Inserts questions from the JSON file for a given topic into the database.
    """
    conn = connect_db()
    data = load_questions_from_json(topic)  # Load questions from the JSON file for the topic

    try:
        with conn.cursor() as cursor:
            # Loop through the questions for the topic
            questions = data.get(topic, [])
            for question_data in questions:
                question = question_data['question']
                correct_answer = question_data['correct_answer']
                wrong_answers = question_data['wrong_answers']
                difficulty = question_data['difficulty']
                
                # Ensure we have 5 answers (including correct and wrong answers)
                while len(wrong_answers) < 5:
                    wrong_answers.append(None)

                # Insert the question into the database for the specific topic
                cursor.execute(f"""
                    INSERT INTO {topic} (module, submodule, difficulty, question, correct_answer, 
                    wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4, wrong_answer5) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (topic.capitalize(), "General", difficulty, question, correct_answer, 
                      wrong_answers[0], wrong_answers[1], wrong_answers[2], 
                      wrong_answers[3], wrong_answers[4]))

            conn.commit()
            print(f"☺️ Questions for {topic} added successfully from JSON file.")
    
    except (Exception, pg.DatabaseError) as e:
        print(f"Error inserting data for {topic}: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    # Loop over the topics and insert questions for each one
    topics = ["geography", "history", "literature", "languages", "general_knowledge"]
    for topic in topics:
        insert_questions_from_json(topic)
