from urllib.parse import urlparse, parse_qs, unquote
from pathlib import Path
import os
from bs4 import BeautifulSoup
from tqdm import tqdm

# Hay que instalarle la dependencia a parte para el sistema operativo
import mimetypes

def marcar_como_descargado(url, cursor,cnx):
    cursor.execute("UPDATE links SET downloaded=1 WHERE url= ?",(url,))
    cnx.commit()

def marcar_como_no_descargable(url, cursor,cnx):
    cursor.execute("UPDATE links SET downloaded=2 WHERE url= ?",(url,))
    cnx.commit()

def obtener_extension_desde_mime(tipo_mime):
    # Mapea tipos MIME conocidos a extensiones
    mime_to_extension = {
        'application/pdf': 'pdf',
        'application/zip': 'zip',
        'application/x-rar-compressed': 'rar',
    }

    # Intenta obtener la extensión del mapeo
    ext = mime_to_extension.get(tipo_mime)

    # Si no se encuentra en el mapeo, utiliza mimetypes para intentar adivinar la extensión
    if not ext:
        ext = mimetypes.guess_extension(tipo_mime, strict=False)

    return ext

def es_contenido_html(contenido):
    # Utiliza BeautifulSoup para analizar el contenido y determinar si es HTML
    soup = BeautifulSoup(contenido, 'html.parser')
    return soup.find('html') is not None

def obtener_id_desde_url(url):
    # Obtén el ID del query parameter "id" de la URL
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    id_param = query_params.get('id', [''])[0]
    return id_param

def descargar_archivo(url, carpeta_destino, session, cursor,cnx):
    respuesta = session.get(url)

    if respuesta.status_code == 303:
        # Obtiene la nueva ubicación desde el encabezado de la respuesta
        nueva_url = respuesta.headers.get('location')
        if nueva_url:
            # Descarga la nueva ubicación
            return descargar_archivo(nueva_url, carpeta_destino, session, cnx)
        else:
            print(f"No se pudo obtener la nueva ubicación para la URL: {url}")
            return False

    tipo_mime = respuesta.headers['content-type'].split(';')[0] 
    extension = obtener_extension_desde_mime(tipo_mime)

    if extension == '.html':
        marcar_como_no_descargable(url,cursor,cnx)
        return False

    # Nombre del archivo dispuesto por el servidor
    if 'Content-Disposition' in respuesta.headers:
        # Obtén el valor del encabezado 'Content-Disposition'
        content_disposition = respuesta.headers['Content-Disposition']

        # Busca la parte que contiene el nombre del archivo
        filename_part = content_disposition.split('filename=')[1]

        # Elimina cualquier carácter adicional (como comillas) que puedan rodear el nombre del archivo
        nombre_archivo = unquote(filename_part).strip('\'"')
    # Si no nos dan el nombre del archivo lo sacamos nostros junto a la etension
    else:
        id_param = obtener_id_desde_url(url)
        if not id_param:
            print(f"No se pudo obtener el ID de la URL: {url}")
            raise Exception("No se pudo obeter el ID de la URL!")
               
        nombre_archivo = f'{id_param}.{extension}'

    print('Descargando', nombre_archivo)

    # Construye la ruta completa del archivo con el ID y la extensión
    ruta_completa = Path(carpeta_destino) / nombre_archivo

    # Asegurarse de que exista la carpeta
    os.makedirs(carpeta_destino, exist_ok=True)

    # Descarga el contenido del archivo y guárdalo
    with open(ruta_completa, 'wb') as archivo:
        archivo.write(respuesta.content)

    marcar_como_descargado(url,cursor,cnx)




def download_all(cnx,session):
    # MAIN
    os.makedirs('./downloads', exist_ok=True)

    cursor = cnx.cursor()

    cursor.execute('''
        SELECT links.url, cursos.fullname FROM links
        JOIN cursos ON cursos.id=links.curso_id
        WHERE links.downloaded = 0;
    ''')
    fetched = cursor.fetchall()

    print('Descargando los archivos pendientes')
    for url in tqdm(fetched):
        # El 1 es el nombre de la asignatura
        carpeta_destino = f'./downloads/{url[1]}'
        # Descargar el archivo
        descargar_archivo(url[0], carpeta_destino, session, cursor, cnx)

    cnx.close()
