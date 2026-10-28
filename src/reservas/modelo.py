import json
import re
from datetime import datetime
from pathlib import Path

_FORMATO_FECHA = "%Y-%m-%d %H:%M"
_PATRON_FECHA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}")
_RUTA_INVENTARIO = Path(__file__).resolve().parents[2] / "data" / "inventario.json"

with _RUTA_INVENTARIO.open(encoding="utf-8") as archivo:
    INVENTARIO: dict[str, str] = {
        unidad["id"]: unidad["equipo"] for unidad in json.load(archivo)
    }


def _parsear_fecha(fecha: str) -> datetime:
    if not isinstance(fecha, str) or _PATRON_FECHA.fullmatch(fecha) is None:
        raise ValueError("La fecha debe tener el formato AAAA-MM-DD HH:MM.")

    try:
        return datetime.strptime(fecha, _FORMATO_FECHA)
    except ValueError as error:
        raise ValueError(
            "La fecha debe tener el formato AAAA-MM-DD HH:MM y ser válida."
        ) from error


def validar_reserva(
    unidad_id: str, solicitante: str, inicio: str, fin: str
) -> None:
    if unidad_id not in INVENTARIO:
        raise ValueError(f"La unidad '{unidad_id}' no existe en el inventario.")
    if not isinstance(solicitante, str) or not solicitante.strip():
        raise ValueError("El solicitante no puede estar vacío ni contener solo espacios.")

    inicio_fecha = _parsear_fecha(inicio)
    fin_fecha = _parsear_fecha(fin)
    if inicio_fecha >= fin_fecha:
        raise ValueError("El inicio debe ser anterior al fin.")


def se_superponen(
    unidad_a: str,
    inicio_a: str,
    fin_a: str,
    unidad_b: str,
    inicio_b: str,
    fin_b: str,
) -> bool:
    if unidad_a != unidad_b:
        return False

    inicio_a_fecha = _parsear_fecha(inicio_a)
    fin_a_fecha = _parsear_fecha(fin_a)
    inicio_b_fecha = _parsear_fecha(inicio_b)
    fin_b_fecha = _parsear_fecha(fin_b)

    if inicio_a_fecha >= fin_a_fecha or inicio_b_fecha >= fin_b_fecha:
        raise ValueError("El inicio de cada intervalo debe ser anterior al fin.")

    return inicio_a_fecha < fin_b_fecha and fin_a_fecha > inicio_b_fecha
