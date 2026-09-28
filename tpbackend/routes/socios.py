from flask import Blueprint, jsonify, request

from ..constants import ERROR_SOCIO_NOT_FOUND
from ..services.socios import crear_socio, listar_socios, obtener_socio, actualizar_socio
from ..utils import construir_error_api, validar_id, validar_paginacion
from ..validators.socios import validar_filtros, validar_socio_create, validar_socio_update

socios_bp = Blueprint('socios', __name__)


def _error(error, default_status=400):
    mensaje = error.args[0]

    if len(error.args) > 1: #si tiene mas de ua argumento
        status = error.args[1]
    else:
        status = default_status #400

    return jsonify(mensaje), status

#ejemplo: http://127.0.0.1:5000/api/socios?_limit=1&_offset=2 
#solo muestra 1 registro a a partir de la posicion 2 (que es el elemento 3)
def _links(limit, offset, total):
    links = {'_first': {'href': request.base_url + f'?_limit={limit}&_offset=0'}}
    if offset > 0:
        previous = max(0, offset - limit)
        links['_prev'] = {'href': request.base_url + f'?_limit={limit}&_offset={previous}'}
    if offset + limit < total:
        links['_next'] = {'href': request.base_url + f'?_limit={limit}&_offset={offset + limit}'}
    if total:
        last = max(0, ((total - 1) // limit) * limit)
    else:
        last = 0
    links['_last'] = {'href': request.base_url + f'?_limit={limit}&_offset={last}'}
    return links


@socios_bp.route('/socios', methods=['GET'])
def get_socios():
    try:
        nombre, activo = validar_filtros(request.args)
        limit, offset = validar_paginacion(request.args.get('_limit'), request.args.get('_offset'))
        socios, total = listar_socios(nombre, activo, limit, offset)
    except ValueError as error:
        return _error(error)
    if not socios:
        return '', 204
    return jsonify({'socios': socios, '_links': _links(limit, offset, total)})


@socios_bp.route('/socios', methods=['POST'])
def post_socio():
    try:
        socio = crear_socio(validar_socio_create(request.get_json(silent=True)))
    except ValueError as error:
        return _error(error)
    return jsonify(socio), 201


@socios_bp.route('/socios/<id>', methods=['GET'])
def get_socio(id):
    try:
        socio = obtener_socio(validar_id(id))
    except ValueError as error:
        return _error(error)
    if not socio:
        return jsonify(construir_error_api(ERROR_SOCIO_NOT_FOUND, 'Socio no encontrado', 'No existe el socio solicitado')), 404
    return jsonify(socio)


@socios_bp.route('/socios/<id>', methods=['PATCH'])
def patch_socio(id):
    try:
        socio_id = validar_id(id)
        socio = actualizar_socio(socio_id, validar_socio_update(request.get_json(silent=True)))
    except ValueError as error:
        return _error(error)
    if not socio:
        return jsonify(construir_error_api(ERROR_SOCIO_NOT_FOUND, 'Socio no encontrado', 'No existe el socio solicitado')), 404
    return '', 204
