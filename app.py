from flask import Flask, request, jsonify
import psycopg2

app = Flask('__name__')

# Define configuration for the database
app.config['DATABASE'] = {
    'host': 'localhost',
    'port': '5432',
    'database': 'million',
    'user': 'postgres',
    'password': 'postgres'
}

# Establish connection with database
def get_db():
    conn = psycopg2.connect(
        host=app.config['DATABASE']['host'],
        port=app.config['DATABASE']['port'],
        dbname=app.config['DATABASE']['database'],
        user=app.config['DATABASE']['user'],
        password=app.config['DATABASE']['password']
    )
    return conn

# Post new message to database
@app.route('/messages', methods=['POST'])
def create_message():
    message = request.json.get('message')

    conn = get_db()
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
    conn = get_db()
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