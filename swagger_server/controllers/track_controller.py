import connexion
import base64
import six
import io

from flask import send_file
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.track import Track  # noqa: E501
from swagger_server import util
from swagger_server.controllers.dbconx.tempName import dbConectar, dbDesconectar
from swagger_server.controllers.authorization_controller import is_valid_token
import psycopg2 as DB


def check_auth(required_scopes=None):
    """
    Verifica autenticación defensiva (backup de Connexion).
    Devuelve (authorized, error_response) tuple.
    """
    token = connexion.request.cookies.get('oversound_auth')
    if not token or not is_valid_token(token):
        error = Error(code="401", message="Unauthorized: Missing or invalid token")
        return False, (error, 401)
    return True, None

def add_track(body):
    """Add a new track to the database"""
    # Verificar autenticación defensiva
    authorized, error_response = check_auth(required_scopes=['write:tracks'])
    if not authorized:
        return error_response
    
    if not connexion.request.is_json:
        return Error(code="400", message="Invalid JSON"), 400

    track = Track.from_dict(connexion.request.get_json())
    conexion = None

    try:
        conexion = dbConectar()
        if not conexion:
            return Error(code="500", message="Database connection failed"), 500

        # Decodificar el base64 a bytes para almacenar en BYTEA
        try:
            track_bytes = base64.b64decode(track.track)
        except Exception as e:
            return Error(code="400", message="Invalid base64 encoding"), 400

        with conexion.cursor() as cur:
            query = "INSERT INTO tracks (track) VALUES (%s) RETURNING idtrack;"
            cur.execute(query, [DB.Binary(track_bytes)])  

            new_id = cur.fetchone()[0]
            conexion.commit()

        # Crear un nuevo objeto Track con el ID generado para la respuesta
        response_track = Track(idtrack=new_id, track=track.track)
        return response_track, 201

    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"Error al crear track: {e}")
        return Error(code="500", message="Database error"), 500

    finally:
        if conexion:
            dbDesconectar(conexion)


def delete_track(track_id):  # noqa: E501
    """Deletes a track.

     # noqa: E501

    :param track_id: 
    :type track_id: int

    :rtype: None
    """
    return 'do some magic!'


def get_track(track_id):  # noqa: E501
    """Gets a track info by idtrack

     # noqa: E501

    :param track_id: 
    :type track_id: int

    :rtype: Track
    """
    return 'do some magic!'


def update_track(body, track_id):
    """Updates a track in the database"""
    # Verificar autenticación defensiva
    authorized, error_response = check_auth(required_scopes=['write:tracks'])
    if not authorized:
        return error_response
    
    if not connexion.request.is_json:
        return Error(code="400", message="Invalid JSON"), 400

    track = Track.from_dict(connexion.request.get_json())
    conexion = None

    try:
        conexion = dbConectar()
        if not conexion:
            return Error(code="500", message="Database connection failed"), 500

        # Decodificar el base64 a bytes para almacenar en BYTEA
        try:
            track_bytes = base64.b64decode(track.track)
        except Exception as e:
            return Error(code="400", message="Invalid base64 encoding"), 400

        with conexion.cursor() as cur:
            query = "UPDATE tracks SET track = %s WHERE idtrack = %s;"
            cur.execute(query, [DB.Binary(track_bytes), track_id])

            if cur.rowcount == 0:
                conexion.rollback()
                return Error(code="404", message="Track not found"), 404

            conexion.commit()

        return '', 204

    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"Error al actualizar track: {e}")
        return Error(code="500", message="Database error"), 500

    finally:
        if conexion:
            dbDesconectar(conexion)

