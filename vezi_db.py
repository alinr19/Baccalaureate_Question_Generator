import sqlite3

DB_FILE = 'bac_exe.db'

try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM exercitii")
    rows = cursor.fetchall()

    print(f"\n---DATABASE CONTENT ({DB_FILE}) ---")
    print(f"Total records: {len(rows)}\n")
    
    if len(rows) == 0:
        print("Database is empty.")
    else:
        for row in rows:
            print(f"ID: {row[0]}")
            print(f"Materia: {row[1]}")
            print(f"Subiect: {row[2]} | {row[3]}")
            print(f"Enunt: {row[4][:50]}...")
            print("-" * 50)

    conn.close()
    input("\nPress Enter to exit.")

except Exception as e:
    print(f"Error: {e}")