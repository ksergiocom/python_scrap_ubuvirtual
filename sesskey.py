from bs4 import BeautifulSoup

def encontrarSesskey(session):
    response_courses_php = session.get('https://ubuvirtual.ubu.es/my/courses.php')
    soup = BeautifulSoup(response_courses_php.text, 'html.parser')

    # Encontrar el script dentro del HTML
    script_tag = soup.find('script', string=lambda s: 'var M = {}; M.yui = {}' in s)

    # Verificar si se encontró el script y extraer el valor de sesskey
    if script_tag:
        script_content = script_tag.string
        sesskey_start = script_content.find('"sesskey":"') + len('"sesskey":"')
        sesskey_end = script_content.find('"', sesskey_start)
        sesskey_value = script_content[sesskey_start:sesskey_end]
    else:
        raise Exception('No se ha encontrado la sesskey')

    return sesskey_value