from datetime import datetime
from database import get_connection

def log_access(name, status):
    conn = get_connection()
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO access_logs (name, status, timestamp) VALUES (?, ?, ?)", (name, status, timestamp))
    conn.commit()
    conn.close()

    print(f"📌 Log enregistré : {name} - {status} à {timestamp}")
