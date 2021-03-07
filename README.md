# Elige tu propia aventura - BOT

Bot desarrollado en Python 3 que publica automáticamente los libros de la saga *Elige tu propia aventura* en Twitter, generando encuestas públicas a la hora de elegir entre capítulos.

## Instalación

### Twitter API 
Es necesario contar con una [cuenta de desarrollador](https://developer.twitter.com/en) en Twitter. Puede tardar hasta 1 semana en ser aprobada. Una vez activada, completar el archivo de `credentials.py.temp` y renombrar a `credentials.py`.

### Instalación de bibliotecas para Python
[Instalar](https://rukbottoland.com/blog/tutorial-de-python-virtualenv/) VirtualEnv para manejar las dependencias, y luego de activar el entorno virtual correr:
```pip install -r requirements.txt```

### Selenium (Ubuntu)
Para instalar Selenium (en Ubuntu):
```sudo apt-get install chromium-chromedriver```

## Cargar libros
Transformar los PDF en secuencia de imágenes, que incluyan el número de página en el nombre respetando el formato ddd (tres digitos, ej: 008,012,145) y construir, en una carpeta aparte dentro del directorio *books* el archivo `guide.json` siguiendo el ejemplo que se encuentra actualmente en el repositorio. Para mayor facilidad a la hora de construir la guía recomiendo eliminar todas las páginas que sobren al principio para que el número de página se corresponda con el número en el nombre de archivo. (001 sería parte del nombre de la imagen de la página 1 de la aventura).

## Uso

Programar ejecución de tarea periódica de `main.py` para automatizar la actualización del bot.
