def get_cursos(session, sesskey):
    # Definir la URL del servicio
    url_cursos = f'https://ubuvirtual.ubu.es/lib/ajax/service.php?sesskey={sesskey}&info=core_course_get_enrolled_courses_by_timeline_classification'

    # Definir los datos que se enviarán en la solicitud POST
    payload = [
        {
            "index": 0,
            "methodname": "core_course_get_enrolled_courses_by_timeline_classification",
            "args": {
                "offset": 0,
                "limit": 0,
                "classification": "all",
                "sort": "fullname",
                "customfieldname": "",
                "customfieldvalue": ""
            }
        }
    ]

    # Crear el cuerpo JSON de la solicitud POST
    json_data = {
        'sesskey': sesskey,
        'info': 'core_course_get_enrolled_courses_by_timeline_classification',
        'args': payload
    }

    # Definir los encabezados de la solicitud POST
    headers = {
        'Content-Type': 'application/json',
    }
    session.headers.update(headers)

    # Realizar la solicitud POST con el cuerpo JSON
    response = session.post(url_cursos, json=payload)

    JSON_dict = response.json()

    if JSON_dict[0]['error']:
        raise Exception('El JSON del server devuelve un error')

    return JSON_dict[0]['data']['courses']
