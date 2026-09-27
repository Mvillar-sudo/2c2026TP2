
from flask import Blueprint, request, jsonify
from mysql.connector import Error as MySQLError

from tpbackend.utils import construir_error_api, construir_links, manejar_error, validar_id
from tpbackend.validators.reservas import (
    validar_filtros_listado, validar_creacion, validar_cambio_estado,
)
from tpbackend.repositories.reservas import (
    listar_reservas, obtener_reserva, crear_reserva, cambiar_estado,
)

reservas_bp = Blueprint("reservas", __name__)

ERROR_RESERVA_NOT_FOUND = 'reserva.not.found'


def _error_bd(e):
    return jsonify(construir_error_api(
        'internal.error', 'Error interno', str(e),
    )), 500



@reservas_bp.route("/reservas", methods=["GET"])
def get_reservas():
    try:
        filtros = validar_filtros_listado(request.args)
    except ValueError as error:
        return manejar_error(error)

    try:
        reservas, total, filtros_url = listar_reservas(filtros)
    except MySQLError as e:
        return _error_bd(e)

    links = construir_links(filtros["_limit"], filtros["_offset"], total,
                             "&".join(filtros_url))
    return jsonify({"reservas": reservas, "_links": links})


@reservas_bp.route("/reservas/<id>", methods=["GET"])
def get_reserva(id):
    try:
        reserva_id = validar_id(id)
        reserva = obtener_reserva(reserva_id)
    except ValueError as error:
        return manejar_error(error)
    except MySQLError as e:
        return _error_bd(e)

    if not reserva:
        return jsonify(construir_error_api(
            ERROR_RESERVA_NOT_FOUND, 'Reserva no encontrada',
            f"No existe una reserva con id {reserva_id}",
        )), 404

    return jsonify(reserva)


@reservas_bp.route("/reservas", methods=["POST"])
def post_reserva():
    try:
        datos = validar_creacion(request.get_json(silent=True))
        reserva = crear_reserva(datos)
    except ValueError as error:
        return manejar_error(error)
    except MySQLError as e:
        return _error_bd(e)

    return jsonify(reserva), 201




@reservas_bp.route("/reservas/<id>/estado", methods=["PUT"])
def put_reserva_estado(id):
    try:
        reserva_id = validar_id(id)
        estado_nuevo = validar_cambio_estado(request.get_json(silent=True))
        reserva = cambiar_estado(reserva_id, estado_nuevo)
    except ValueError as error:
        return manejar_error(error)
    except MySQLError as e:
        return _error_bd(e)

    if not reserva:
        return jsonify(construir_error_api(
            ERROR_RESERVA_NOT_FOUND, 'Reserva no encontrada',
            f"No existe una reserva con id {reserva_id}",
        )), 404

    return jsonify(reserva)