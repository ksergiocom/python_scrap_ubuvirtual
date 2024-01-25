from login import hacerLoginYcrearSession
from sesskey import encontrarSesskey
from get_cursos import get_cursos
from contenido_curso import get_contenido
from db import db_connect
from tqdm import tqdm
from download import download_all

session, loged = hacerLoginYcrearSession().values()

if loged:
    [cnx, cursor] = db_connect()

    # Necesario para operar con el servicio AJAX que usan para la web
    sesskey = encontrarSesskey(session)

    # Links de los cursos del usario actual
    cursos = get_cursos(session,sesskey)
    
    print('Buscando cursos disponibles...')
    for curso in tqdm(cursos):
        print('Ejecutando -> '+curso['fullname'])

        # Verificar si el curso ya existe en la base de datos
        cursor.execute('SELECT id, url FROM cursos WHERE fullname = ?', (curso['fullname'],))
        result = cursor.fetchone()

        if result:
            # El curso ya existe, obtener su id
            curso_id = result[0]
        else:
            # El curso no existe, insertarlo en la base de datos
            cursor.execute('INSERT INTO cursos (fullname, url) VALUES (?, ?)',
                            (curso['fullname'],curso['viewurl']))
            cnx.commit()
            curso_id = cursor.lastrowid
            print(f'Nuevo curso -> {curso["fullname"]}')

        get_contenido(session,curso['viewurl'],curso_id,cursor)

    download_all(cnx,session)

    # No manejo los errores! Ya se cerrará solo. LOL
    cnx.close()