import sqlite3

def db_connect():
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()

    # En SQLite no existe el BOOLEAN, lolazo.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            fecha TEXT,
            curso_id INTEGER,
            downloaded INTEGER DEFAULT 0,
            FOREIGN KEY (curso_id) REFERENCES cursos(id)
        )
    ''')

    # Crear la tabla de cursos si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cursos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT,
            url TEXT
        )
    ''')

    conn.commit()
    return conn, cursor