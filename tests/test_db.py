import psycopg

conn = psycopg.connect("host=localhost dbname=warehouse user=postgres password=postgres", autocommit=True)
print("Подключение успешно!")
conn.close()
