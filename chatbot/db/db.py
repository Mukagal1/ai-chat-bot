import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

cursor.execute("""select * from auth_user""")
tables = cursor.fetchall()

for table in tables:
	print(table)
	print(table[1])