import psycopg2
import json

# Load database configuration
with open('database-config.json', 'r') as f:
    config = json.load(f)

try:
    # Connect to the database
    conn = psycopg2.connect(
        host=config['host'],
        port=config['port'],
        user=config['user'],
        password=config['password'],
        database=config['database']
    )
    
    cursor = conn.cursor()
    
    # Check if there are any users
    cursor.execute("SELECT id, email, firstname, lastname FROM users;")
    users = cursor.fetchall()
    
    print("Existing users in the database:")
    for user in users:
        print(f"ID: {user[0]}, Email: {user[1]}, Name: {user[2]} {user[3]}")
    
    # Check if there are any data records
    cursor.execute("SELECT COUNT(*) FROM data;")
    count = cursor.fetchone()[0]
    print(f"\nNumber of data records: {count}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")