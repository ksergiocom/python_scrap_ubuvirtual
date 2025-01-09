# LOL! -------------------------------------
import os

# Verificar si el archivo _credenciales.py existe, y crearlo si no.
if not os.path.exists("_credenciales.py"):
    with open("_credenciales.py", "w") as f:
        f.write("username=None\npassword=None\n")
    print("Archivo '_credenciales.py' creado. Por favor, rellena tu usuario y contraseña.")
# -------------------------------------------



import requests
from bs4 import BeautifulSoup
import _credenciales
import getpass

def hacerLoginYcrearSession():

    # URL de la página de inicio de sesión
    login_url = 'https://ubuvirtual.ubu.es/login/index.php'

    # Crear una sesión para manejar cookies
    session = requests.Session()

    # Realizar una solicitud GET para obtener la página de inicio de sesión y extraer el token y la cookie
    response_get = session.get(login_url)
    soup = BeautifulSoup(response_get.text, 'html.parser')

    # Encuentra el campo de login token en el formulario (ajusta el nombre del campo según la realidad de la página)
    login_token = soup.find('input', {'name': 'logintoken'})['value']

    # Obtener la cookie MoodleSessionmoodlecurrent de la respuesta
    moodle_session_cookie = session.cookies.get('MoodleSessionmoodlecurrent')

    if _credenciales.password and _credenciales.username:
        username =_credenciales.username 
        password = _credenciales.password 
    else:
        username = input('Introduce tu usuario: ')
        password = getpass.getpass('Introduce tu contraseña: ')

    # Definir las credenciales
    credentials = {
        'anchor': '',
        'username': username,
        'password': password,
        'logintoken': login_token
    }

    # Establecer los headers para la solicitud POST
    post_headers = {
        'Host': 'ubuvirtual.ubu.es',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://ubuvirtual.ubu.es',
        'Connection': 'keep-alive',
        'Referer': 'https://ubuvirtual.ubu.es/',
        'Cookie': f'MoodleSessionmoodlecurrent={moodle_session_cookie}',  # Utiliza la cookie obtenida en la respuesta GET
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
    }

    # Realizar una solicitud POST con las credenciales
    response_post = session.post(login_url, data=credentials, headers=post_headers)

    # Realizar una solicitud GET a la página de perfil
    profile_url = 'https://ubuvirtual.ubu.es/user/profile.php'
    response_profile = session.get(profile_url)

    # Verificar si la sesión está activa: Existe un elemento h4 en la pagina de PROFILE que dice confirmar
    soup_profile = BeautifulSoup(response_profile.text, 'html.parser')
    h4_element = soup_profile.find('h4', text='Confirmar')

    loged = True
    if h4_element:
        loged = False
        print('No se ha podido iniciar sesion.')
        raise Exception('No se ha iniciado sesión! Comprueba las credenciales! (La comprobacion del h4, puede haber cambiado)')

    print('Iniciada sesion correctamente.')
    return {
        'session':session,
        'loged':loged
    }