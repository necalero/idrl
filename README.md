# Desarrollo de software en la nube



## Instalación

Debe contar con la instalación previa de docker para correr esta aplicación.

El primer paso corresponde a clonar el repositorio en el ambiente local

`git clone https://gitlab.com/miso6795741/desarrollo-de-software-en-la-nube.git`

Una vez clonado el repositorio se cuentan con 2 opciones para la construcción del proyecto:
### 1. docke-compose
En la terminal del proyecto base se debe ingresar a la carpeta flaskr

`cd flaskr`

Posteriormente se debe iniciar la aplicación con docker compose

`docker-compose up`

### 2. Crear una imagen docker
En la terminal del proyecto base se debe ingresar a la carpeta flaskr

`cd flaskr`

Crear la imagen a partir del dockerfile.

`docker build -t idrl .`

Correr la imagen en un contenedor.

`docker run -d -p 5000:5000 idrl`

## Pruebas Postman

El proyecto cuenta con un archivo 'Proyecto Desarrollo de Software en la Nube.postman_collection.json' el cual corresponde a una colección de postman que cuenta con la documentación y pruebas de los endpoints utilizados en la API. Para hacer uso de esta colección se debe importar en Postman e iniciar previamente la aplicación haciendo uso de Docker como se explicó en el paso anterior

## Información adicional

Puede encontrar información adicional (Arquitectura, video y plan de análisis de capacidad) en la wiki de este repositorio