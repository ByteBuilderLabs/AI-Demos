import sqlite3
conn = sqlite3.connect('demo.db')
conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT)')
conn.execute('DELETE FROM users')
conn.execute('INSERT INTO users VALUES (1, \"Alice\"), (2, \"Bob\")')
conn.commit()
conn.close()
print('Database created successfully')
