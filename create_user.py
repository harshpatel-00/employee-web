import sqlite3

conn = sqlite3.connect('employees.db')
cursor = conn.cursor()

cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'admin123'))
conn.commit()
conn.close()

print("User Added")