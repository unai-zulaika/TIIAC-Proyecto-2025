# Proyecto TIIAC asignatura del 2025

La definición de proyecto es accesible [aquí](https://docs.google.com/document/d/1R7f3bryEZusEhZnr552xt6Ojv1kPPOL7kzcdy8zFrOI/edit?usp=sharing).

---

## **Crear e inicializar la base de datos**

### Levantar la base de datos con Docker
1. Abre CMD o terminal en la carpeta donde se encuentra el archivo `docker-compose.yml`.
2. Ejecuta el siguiente comando:
```bash
docker compose up -d
```
3. En la carpeta src/backend/DB, inicializar la base de datos usando el archivo: 
```bash
init.sql
```
4. En la misma carpeta, ejecutar el script de la ETL para poder subir los datos a la base de datos.

### Borrar el contenedor junto con la base de datos
1. Abre CMD o terminal en la carpeta donde se encuentra el archivo `docker-compose.yml`.
2. Ejecuta el siguiente comando:
```bash
docker compose down -v
```

## **Iniciar Backend:**
1. En la carpeta src/backend/api, ejecutar el siguiente comando: 
```bash
uvicorn main:app --reload
```
2. Acceder al backend en el puerto del localhost: 
http://127.0.0.1:8000        
O a la documentacion con swagger:
http://127.0.0.1:8000/docs#/
