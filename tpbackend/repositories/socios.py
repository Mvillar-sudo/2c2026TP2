from sqlalchemy import create_engine, text

from ..constants import DB_URL

motor = create_engine(DB_URL, pool_pre_ping=True)


def ejecutar_consulta(sql: str, parametros=None):
    with motor.connect() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})
        return [dict(fila._mapping) for fila in resultado]


def ejecutar_mutacion(sql: str, parametros=None):
    with motor.begin() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})
        return resultado.rowcount


def obtener_socios(nombre=None, activo=None, limit=10, offset=0):
    condiciones = []
    parametros = {'limit': limit, 'offset': offset}
    if nombre:
        condiciones.append('LOWER(nombre_socio) LIKE :nombre')
        parametros['nombre'] = f'%{nombre.lower()}%'
    if activo is not None:
        condiciones.append('socio_activo = :activo')
        parametros['activo'] = activo
    if condiciones:
        clause = f"WHERE {' AND '.join(condiciones)}"
    else:
        clause = ''
    sql = f"""
        SELECT id_socio, nombre_socio, email, socio_activo
        FROM socios
        {clause}
        ORDER BY id_socio
        LIMIT :limit OFFSET :offset
    """
    return ejecutar_consulta(sql, parametros)


def contar_socios(nombre=None, activo=None):
    condiciones = []
    parametros = {}
    if nombre:
        condiciones.append('LOWER(nombre_socio) LIKE :nombre')
        parametros['nombre'] = f'%{nombre.lower()}%'
    if activo is not None:
        condiciones.append('socio_activo = :activo')
        parametros['activo'] = activo
    if condiciones:
        clause = f"WHERE {' AND '.join(condiciones)}"
    else:
        clause = ''
    filas = ejecutar_consulta(
        f'SELECT COUNT(*) AS total FROM socios {clause}',
        parametros)
    return filas[0]['total']


def obtener_socio(id_socio):
    filas = ejecutar_consulta(
        'SELECT id_socio, nombre_socio, email, socio_activo FROM socios WHERE id_socio = :id',
        {'id': id_socio},
    )
    if filas:
        return filas[0]
    else:
        return None


def obtener_socio_por_email(email, excluir_id=None):
    sql = 'SELECT id_socio FROM socios WHERE email = :email'
    parametros = {'email': email}
    if excluir_id is not None:
        sql += ' AND id_socio <> :id'
        parametros['id'] = excluir_id
    filas = ejecutar_consulta(sql, parametros)
    if filas:
        return filas[0]
    else:
        return None


def insertar_socio(nombre_socio, email):
    with motor.begin() as conexion:
        resultado = conexion.execute(
            text(
                'INSERT INTO socios (nombre_socio, email)'
                'VALUES (:nombre_socio, :email)'
            ), {'nombre_socio': nombre_socio, 'email': email})
        return resultado.lastrowid


def modificar_socio(id_socio, datos):
    lista_asignaciones = []

    for campo in datos:
        lista_asignaciones.append(f'{campo} = :{campo}')
    asignaciones = ', '.join(lista_asignaciones)
    parametros = {**datos, 'id': id_socio}

    return ejecutar_mutacion(
        f'UPDATE socios SET {asignaciones} WHERE id_socio = :id', parametros
    )
