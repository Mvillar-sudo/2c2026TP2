# TP2-Backend
# Proyecto Backend: Sistema de reservas de club deportivo
### Introducción al Desarrollo de Software  - Curso Lanzillota 

Este repositorio contiene la API REST desarrollada para la gestión de la reserva de canchas para un club deportivo siguiendo lo solicitado por el **enunciado**.

##  Estructura del Proyecto

* `app.py`: Punto de entrada del servidor Flask y definición de rutas.
* `swagger.yaml`: Contrato de la API que define los estándares de entrada y salida.
* `requiremnt.txt`: Librerias necesarias.
* `docker-compose.yml`: Permite comunicacion entre base de datos y el servidor

##  Tecnologías Utilizadas
* **Lenguaje:** Python 3.10+
* **Framework:** Flask
* **Base de Datos:** MySQL

## Endpoints Principales

## Endpoints implementados

# API DE SOCIOS

- `GET /socios`: listado paginado con `nombre`, `activo`, `_limit` y `_offset`.
- `POST /socios`: crea un socio con `nombre` y `email`.
- `GET /socios/{id}`: obtiene un socio.
- `PATCH /socios/{id}`: actualiza parcialmente `nombre`, `email` o `activo`.

##  Dependencias
Es necesario instalar el microframework Flask y el conector para MySQL:
```bash
pip install Flask mysql-connector-python
```
## Puesta en marcha

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose up -d
python3 app.py
```

# Adicional

- Asegurate de no tener levantado algun otro proyecto en el mismo puerto que la base de datos antes de correr el backend
- Para correr la app: http://127.0.0.1:8080/api/
