## Como usar
Crear el entorno virtual, instalar dependencias y a correr!

```
cd ./ruta-del-proyecto

python -m venv venv

# Linux
source venv/bin/activate
# Windows
.\venv\Scripts\activate o .\venv\Scripts\Activate

pip install -r requirements.txt

python main.py
```

## ¿Que es esto?

He creado un scraper que descarga todos los recursos de mis cursos en la universidad. [Aquí dejo el repositorio ](https://github.com/ksergiocom/python_scrap_ubuvirtual)

El código es bastante caotico porque ha ido creciendo de forma organica. Según se me ocurría lo iba agregando. Al ser tan poca cosa no me he tomado la molestia en refactorizarlo ni dejarlo bonito. Simplemente funciona, y ya.

## Iniciar sesión con Python
Usando la librería de **requests** de python podemos hacer peticiones HTTP para solicitar recursos al servidor. Esta librería nos facilita el manejo de cookies o redirecciones para peticiones recurrentes.

Lo primero que tenemos que hacer es iniciar sesión en la web con nuestras credenciales. El primer problema es que no podemos hacer un simple POST con las credenciales.

El formulario tiene dos campos "hidden" **logintoken** y **anchor**. Login token es un token generado aleatoriamente por el servidor a modo de protección CSRF.

Por otro lado la plataforma Moodle usa su propia cookie a modo de sesión. Tenemos que tener esto en cuenta a la hora de mandar nuestras peticiones.

Lo primero que hacemos es iniciarlizar un objeto sesión con python requests, que guardará las cookies para reutilizar de forma automática, evitando tener que pasarla por las cabeceras constantemente.

```
session  =  requests.Session()
```

A continuación simplemente hacemos una peticion GET al formulario y sacamos el token CSRF.

```
# URL de la página de inicio de sesión
login_url  =  'https://ubuvirtual.ubu.es/login/index.php'

# Realizar una solicitud GET para obtener la página de inicio de sesión y extraer el token y la cookie
response_get  =  session.get(login_url)
soup  =  BeautifulSoup(response_get.text, 'html.parser')

# Encuentra el campo de login token en el formulario (ajusta el nombre del campo según la realidad de la página)
login_token  =  soup.find('input', {'name': 'logintoken'})['value']
```
 Con todo esto ya si que podemos hacer un POST con nuestros datos

```
# El paquete getpass nos permite ingresar la contraseña de forma oculta por terminal
username  =  input('Introduce tu usuario: ')
password  =  getpass.getpass('Introduce tu contraseña: ')
```

Podemos por otro lado tener las credenciales guardadas de forma externa e importarlas.

Para simular que hago la petición desde un browser y que no me ponga pegas el servidor, le asigno cabeceras simulando una petición desde el navegador. *Esto solo es necesario si se queja el servidor*.

```
# Establecer los headers para la solicitud POST

post_headers  = {
	'Host': 'ubuvirtual.ubu.es',
	'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
	'Accept-Language': 'en-US,en;q=0.5',
	'Accept-Encoding': 'gzip, deflate, br',
	'Content-Type': 'application/x-www-form-urlencoded',
	'Origin': 'https://ubuvirtual.ubu.es',
	'Connection': 'keep-alive',
	'Referer': 'https://ubuvirtual.ubu.es/',
	'Cookie': f'MoodleSessionmoodlecurrent={moodle_session_cookie}', # Utiliza la cookie obtenida en la respuesta GET
	'Upgrade-Insecure-Requests': '1',
	'Sec-Fetch-Dest': 'document',
	'Sec-Fetch-Mode': 'navigate',
	'Sec-Fetch-Site': 'same-origin',
	'Sec-Fetch-User': '?1',
}

# Realizar una solicitud POST con las credenciales
response_post  =  session.post(login_url, data=credentials, headers=post_headers)
```

Lo ultimo que faltaría sería comprobar de alguna forma si se ha conseguido acceder o no. Conociendo la pagina de error, simplemente podemos comprobar si aparece algun elemento de confirmación de error, o nos redirige a una pagina interna.

## Servicio AJAX
Cuando accedes dentro de la página los cursos no aparecen directamente, si no que se cargan a través de un servicio AJAX que rellena los datos a posteriori.

Localizado el endopoint al que se tiene que realizar la llamada, veo que se tiene que pasar otra nueva clave. Esta vez es una Sesskey que se asigna a nuestra nueva sesión.

Rebuscando he encontrado que viene en un script dentro de la misma página. Con este scritp podemos filtrar el contenido hasta dar con la **sesskey**

```
# Encontrar el script dentro del HTML
script_tag  =  soup.find('script', string=lambda  s: 	'var M = {}; M.yui = {}'  in  s)

# Verificar si se encontró el script y extraer el valor de sesskey
if  script_tag:
	script_content  =  script_tag.string
	sesskey_start  =  script_content.find('"sesskey":"') +  len('"sesskey":"')
	sesskey_end  =  script_content.find('"', sesskey_start)
	sesskey_value  =  script_content[sesskey_start:sesskey_end]
else:
	raise  Exception('No se ha encontrado la sesskey')
```

Ahora solo hace falta hacer el POST con la codificación correcta. Los argumentos del JSON enviado los sabemos porque la petición se lanza de forma automática al cargar la página.

```
# Definir los datos que se enviarán en la solicitud POST

payload  = [
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
```
La respuesta que nos da nos proporciona un array de cursos a los que estamos suscritos, con algunos datos incluidos los links hacia ellos.

## Scraping de recursos
Recorriendo los links que nos llega desde este servicio podemos acceder directamente a la pagina donde se presentan los recursos de la asignatura.

Aquí me he dado cuenta que todos los links de recursos vienen con una clase css *aalink*. Así que no queda más que scrapear estas lineas y sacar las urls.

```
# Los links del contenido que suben tienen todos la clase: "aalink"
aalink_elements  =  soup.find_all('a', class_='aalink')

# Extrae los valores del atributo 'href' de cada elemento
href_values  = [element.get('href') for  element  in  aalink_elements  if  element.get('href') and  element.get('href') !=  '#']
```


## Descarga de archivos y extensiones
En mi caso he decidido guardar los links en una base de datos de sqlite para llevar un registro de cuando los he encontrado y si se han descargado ya.

Itero sobre los links y saco el tipo de archivo así como su nombre con las cabeceras. Aquí un ejemplo simple de como extraer el mimetipo desde cabeceras o con la libreria mimetype de python.

Como bonus, se podría buscar a travez del **file magic** para encontrar un patrón de bytes del archivo.

```
def  obtener_extension_desde_mime(tipo_mime):
	# Mapea tipos MIME conocidos a extensiones
	mime_to_extension  = {
		'application/pdf': 'pdf',
		'application/zip': 'zip',
		'application/x-rar-compressed': 'rar',
	}

	# Intenta obtener la extensión del mapeo
	ext  =  mime_to_extension.get(tipo_mime)

	# Si no se encuentra en el mapeo, utiliza mimetypes para intentar adivinar la extensión
	if  not  ext:
	ext  =  mimetypes.guess_extension(tipo_mime, strict=False)

	return  ext
```
Por ultimo solo queda descargar los archivos y meterlos en una carpeta que deseemos.

## Trucos de optimización

Si scrapeamos el mismo contenido multiples veces y este es consistente. Por ejemplo, en este caso habría que excluir tags de JS porque hay valores relacionados a la sesión. Pero el contenedor de los recursos no varia.

Podemos hashear el contenido HTML y guardar el hash. Las veces consecutivas, al escrapear volvemos a convertir el contenido a un hash y lo comparamos contra el almacenado anteriormente. En caso de que difieran, sabemos que hay nuevo contenido, en caso contrario no.

Esto puede ser eficiente dependiendo del tamaño del archivo, ya que las operaciones de hashear + comparacion entre dos hashes puede ser más corta que comparar bit a bit todo el contenido.
