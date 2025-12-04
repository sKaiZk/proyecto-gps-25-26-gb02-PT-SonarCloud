import psycopg2 as DB
from psycopg2.extensions import connection

def dbconectar() -> connection:
    ip = "pgnweb.ddns.net"
    puerto = 5432
    basedatos = "pt"

    usuario = "pt_admin"
    contrasena = "12345"

    print("---dbconectar---")
    print("---Conectando a Postgresql---")

    try:
        conexion = DB.connect(user=usuario, password=contrasena, host=ip, port=puerto, database=basedatos)
        conexion.autocommit = False
        print("Conexión realizada a la base de datos", conexion)
        return conexion
    except DB.DatabaseError as error:
        print("Error en la conexión")
        print(error)
        return None

def dbdesconectar(conexion):
    print("---dbdesconectar---")
    try:
        conexion.close()
        print("Desconexión realizada correctamente")
        return True
    except DB.DatabaseError as error:
        print("Error en la desconexión")
        print(error)
        return False