from bs4 import BeautifulSoup
from datetime import datetime

def enlace_existe(cursor, enlace):
    cursor.execute('SELECT id FROM links WHERE url = ?', (enlace,))
    resultado = cursor.fetchone()
    return resultado is not None

def get_contenido(session, curso_url, curso_id_db, cursor):
    response_get = session.get(curso_url)
    soup = BeautifulSoup(response_get.text, 'html.parser')

    # Los links del contenido que suben tienen todos la clase: "aalink"
    aalink_elements = soup.find_all('a', class_='aalink')

    # Extrae los valores del atributo 'href' de cada elemento
    href_values = [element.get('href') for element in aalink_elements if element.get('href') and element.get('href') != '#']

    now = datetime.now()
    data_to_insert = [(href, now, curso_id_db) for href in href_values if not enlace_existe(cursor, href)]

    for link in data_to_insert:
        print('Insertando nuevo link -> ',link[0])

    if data_to_insert:
        cursor.executemany('''
            INSERT INTO links (url, fecha, curso_id)
            VALUES (?, ?, ?)
        ''', data_to_insert)

        # Realizas un commit para guardar los cambios en la base de datos
        cursor.connection.commit()