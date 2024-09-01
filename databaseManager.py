# DatabaseManager.py
import mysql.connector

# Establecer la conexión con la base de datos MySQL

mydb = mysql.connector.connect(
    host="localhost",  # Dirección del servidor de la base de datos
    user="root",       # Usuario de la base de datos
    password="",       # Contraseña del usuario de la base de datos
    port="3306",       # Puerto de la base de
    database="colegio" # Nombre de la base de datos
)

# Crear un cursor para ejecutar las consultas SQL
cursor = mydb.cursor()

def close_connection():
    """
    Cierra la conexión con la base de datos.
    """
    cursor.close()
    mydb.close()
