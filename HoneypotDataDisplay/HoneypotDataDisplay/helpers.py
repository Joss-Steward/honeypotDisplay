import psycopg2
from HoneypotDataDisplay import settings

def query(query, args=(), one=False):
    conn = psycopg2.connect(settings.ConnectionString)
    cursor = conn.cursor()
    cursor.execute(query, args)

    result = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]

    conn.commit()
    conn.close()
    return (result[0] if result else None) if one else result