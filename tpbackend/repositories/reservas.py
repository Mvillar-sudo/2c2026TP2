
from datetime import datetime, timezone, timedelta

from db import get_connection
from tpbackend.utils import construir_error_api

ZONA_GMT3 = timezone(timedelta(hours=-3))

# Mapea cada filtro posible a su condición SQL. El orden de este
# diccionario también define el orden en que se arma el WHERE.
_CONDICIONES_SQL = {
    "id_cancha": "id_cancha = %s",
    "id_socio": "id_socio = %s",
    "estado": "estado = %s",
    "fecha_desde": "DATE(fecha_hora_inicio) >= %s",
    "fecha_hasta": "DATE(fecha_hora_inicio) <= %s",
}



def _formatear_fecha(dt):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZONA_GMT3)
    return dt.isoformat(timespec="microseconds")

def _fila_a_json(fila):
    return {
        "id": fila["id_reserva"],
        "id_socio": fila["id_socio"],
        "id_cancha": fila["id_cancha"],
        "fecha_hora_inicio": _formatear_fecha(fila["fecha_hora_inicio"]),
        "fecha_hora_fin": _formatear_fecha(fila["fecha_hora_fin"]),
        "estado": fila["estado"],
        "precio_hora": fila["precio_hora_historico"],
        "precio_total": fila["total"],
    }


def listar_reservas(filtros):
    condiciones = []
    valores = []
    filtros_url = []

    for clave, condicion_sql in _CONDICIONES_SQL.items():
        if clave in filtros:
            condiciones.append(condicion_sql)
            valores.append(filtros[clave])
            filtros_url.append(f"{clave}={filtros[clave]}")

    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
    limit = filtros["_limit"]
    offset = filtros["_offset"]

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(f"SELECT COUNT(*) as total FROM reservas {where}", tuple(valores))
        total = cursor.fetchone()["total"]

        cursor.execute(
            f"""
            SELECT * FROM reservas {where}
            ORDER BY id_reserva ASC
            LIMIT %s OFFSET %s
            """,
            tuple(valores + [limit, offset]),
        )
        filas = cursor.fetchall()

        return [_fila_a_json(f) for f in filas], total, filtros_url
    finally:
        if conn is not None:
            conn.close()


def obtener_reserva(id_reserva):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM reservas WHERE id_reserva = %s", (id_reserva,))
        fila = cursor.fetchone()
        return _fila_a_json(fila) if fila is not None else None
    finally:
        if conn is not None:
            conn.close()



def crear_reserva(datos):
    id_socio = datos["id_socio"]
    id_cancha = datos["id_cancha"]
    inicio = datos["fecha_hora_inicio"]
    fin = datos["fecha_hora_fin"]

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT socio_activo FROM socios WHERE id_socio = %s", (id_socio,))
        socio = cursor.fetchone()
        if socio is None:
            raise ValueError(construir_error_api(
                'socio.not.found', 'Socio no encontrado',
                f"No existe un socio con id_socio={id_socio}",
            ), 404)
        if not socio["socio_activo"]:
            raise ValueError(construir_error_api(
                'socio.inactivo', 'Socio inactivo',
                'No se pueden crear reservas para un socio inactivo',
            ), 409)

        cursor.execute("SELECT cancha_activa, precio_hora FROM canchas WHERE id_cancha = %s",
                       (id_cancha,))
        cancha = cursor.fetchone()
        if cancha is None:
            raise ValueError(construir_error_api(
                'cancha.not.found', 'Cancha no encontrada',
                f"No existe una cancha con id_cancha={id_cancha}",
            ), 404)
        if not cancha["cancha_activa"]:
            raise ValueError(construir_error_api(
                'cancha.inactiva', 'Cancha inactiva',
                'No se pueden crear reservas para una cancha inactiva',
            ), 409)

        # A partir de acá se compara/guarda "naive" (sin tzinfo), porque
        # así están guardadas las fechas en la tabla (columnas DATETIME,
        # todas asumidas en GMT-3 por convención del proyecto).
        inicio_naive = inicio.replace(tzinfo=None)
        fin_naive = fin.replace(tzinfo=None)

        cursor.execute(
            """
            SELECT id_reserva FROM reservas
            WHERE id_cancha = %s AND estado = 'confirmada'
            AND fecha_hora_inicio < %s AND fecha_hora_fin > %s
            """,
            (id_cancha, fin_naive, inicio_naive),
        )
        if cursor.fetchone() is not None:
            raise ValueError(construir_error_api(
                'cancha.no.disponible', 'Cancha no disponible',
                'La cancha ya tiene una reserva confirmada que se superpone '
                'con el intervalo solicitado',
            ), 409)

        cursor.execute(
            """
            SELECT id_reserva FROM reservas
            WHERE id_socio = %s AND estado = 'confirmada'
            AND fecha_hora_inicio < %s AND fecha_hora_fin > %s
            """,
            (id_socio, fin_naive, inicio_naive),
        )
        if cursor.fetchone() is not None:
            raise ValueError(construir_error_api(
                'socio.no.disponible', 'Socio no disponible',
                'El socio ya tiene una reserva confirmada que se superpone '
                'con el intervalo solicitado',
            ), 409)

        duracion_horas = int((fin_naive - inicio_naive).total_seconds() // 3600)
        precio_hora = cancha["precio_hora"]
        total = duracion_horas * precio_hora

        cursor.execute(
            """
            INSERT INTO reservas
                (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin,
                 estado, precio_hora_historico, total)
            VALUES (%s, %s, %s, %s, 'confirmada', %s, %s)
            """,
            (id_socio, id_cancha, inicio_naive, fin_naive, precio_hora, total),
        )
        conn.commit()
        nuevo_id = cursor.lastrowid

        return {
            "id": nuevo_id,
            "id_socio": id_socio,
            "id_cancha": id_cancha,
            "fecha_hora_inicio": _formatear_fecha(inicio),
            "fecha_hora_fin": _formatear_fecha(fin),
            "estado": "confirmada",
            "precio_hora": precio_hora,
            "precio_total": total,
        }
    finally:
        if conn is not None:
            conn.close()



def cambiar_estado(id_reserva, estado_nuevo):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM reservas WHERE id_reserva = %s", (id_reserva,))
        fila = cursor.fetchone()
        if fila is None:
            return None

        estado_actual = fila["estado"]
        if estado_nuevo == estado_actual:
            return _fila_a_json(fila)

        ahora = datetime.now(ZONA_GMT3).replace(tzinfo=None)
        inicio = fila["fecha_hora_inicio"]
        fin = fila["fecha_hora_fin"]

        permitido = (
            estado_actual == "confirmada" and estado_nuevo == "cancelada" and ahora < inicio
        ) or (
            estado_actual == "confirmada" and estado_nuevo == "finalizada" and ahora >= fin
        )

        if not permitido:
            raise ValueError(construir_error_api(
                'transicion.invalida', 'Transicion no permitida',
                f"No se puede pasar de '{estado_actual}' a '{estado_nuevo}' en este momento",
            ), 409)

        cursor.execute("UPDATE reservas SET estado = %s WHERE id_reserva = %s",
                       (estado_nuevo, id_reserva))
        conn.commit()

        fila["estado"] = estado_nuevo
        return _fila_a_json(fila)
    finally:
        if conn is not None:
            conn.close()