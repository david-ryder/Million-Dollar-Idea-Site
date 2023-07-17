from flask import Flask, request, jsonify
import psycopg2

app = Flask('__name__')

def connect_to_database():
    conn = psycopg2.connect(
        host="db", 
        port=5432,
        user="postgres",
        password="postgres",
        database="million"
    )
    return conn

def create_schema():
    conn = None
    try:
        conn = connect_to_database()
        cur = conn.cursor()

        # Create the 'messages' table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                message TEXT
            );
        """)

        conn.commit()
        cur.close()
        print("Schema created successfully")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error creating schema:", error)
    finally:
        if conn is not None:
            conn.close()

# Call create_schema() when the Flask API connects to the database
with app.app_context():
    create_schema()

# Post new message to database
@app.route('/messages', methods=['POST'])
def create_message():
    message = request.json.get('message')

    conn = connect_to_database()
    cur = conn.cursor()

    try:
        cur.execute('BEGIN')
        cur.execute('INSERT INTO messages (message) VALUES (%s)', (tuple([message])))
        conn.commit()
        cur.close()
        conn.close()
        return "Message inserted successfully!"
    except Exception as e:
        conn.rollback()
        return f"Failed to insert message: {str(e)}"
    finally:
        cur.close()
        conn.close()

# Get all messages from database
@app.route('/messages', methods=['GET'])
def read_messages():
    conn = connect_to_database()
    cur = conn.cursor()

    cur.execute('SELECT * FROM messages')
    rows = cur.fetchall()

    messages = []
    for row in rows:
        message = {
            'id': row[0],
            'message': row[1]
        }
        messages.append(message)

    cur.close()
    conn.close()

    return jsonify(messages)

# Run the API
if __name__ == '__main__':
    app.run(port=5001)