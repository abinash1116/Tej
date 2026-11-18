from database.db_connection import create_task_table, create_connection

create_task_table()

connection = create_connection()
cursor = connection.cursor()

cursor.execute("""
    SELECT name FROM sqlite_master
    WHERE type = 'table'
""")

tables = cursor.fetchall()

for table in tables:
    print(table["name"])

connection.close()