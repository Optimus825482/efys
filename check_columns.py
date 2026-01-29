import psycopg2
conn = psycopg2.connect('postgresql://postgres:518518Erkan@localhost:5432/osos_db')
cur = conn.cursor()
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'alarms'")
print("alarms columns:", [r[0] for r in cur.fetchall()])
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'scheduled_readings'")
print("scheduled_readings columns:", [r[0] for r in cur.fetchall()])
conn.close()
