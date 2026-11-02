import sqlite3
from pathlib import Path

from reservas.modelo import se_superponen, validar_reserva

COLUMNAS = ("id", "unidad", "solicitante", "inicio", "fin", "estado")


class RepositorioReservas:
    """Guarda y recupera reservas en un archivo SQLite."""

    def __init__(self, ruta_archivo: str | Path):
        self.ruta_archivo = Path(ruta_archivo)
        self.ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
        self._conexion = sqlite3.connect(self.ruta_archivo)
        self._conexion.row_factory = sqlite3.Row
        self._crear_tabla()

    def __enter__(self) -> "RepositorioReservas":
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def close(self) -> None:
        """Cierra la conexión con la base."""
        self._conexion.close()

    def _crear_tabla(self) -> None:
        with self._conexion:
            self._conexion.execute(
                """
                CREATE TABLE IF NOT EXISTS reservas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unidad TEXT NOT NULL,
                    solicitante TEXT NOT NULL,
                    inicio TEXT NOT NULL,
                    fin TEXT NOT NULL,
                    estado TEXT NOT NULL CHECK (estado IN ('activa', 'cancelada'))
                )
                """
            )

    @staticmethod
    def _a_diccionario(fila: sqlite3.Row) -> dict:
        return {columna: fila[columna] for columna in COLUMNAS}

    def _validar_intervalo(self, unidad: str, inicio: str, fin: str) -> None:
        validar_reserva(unidad, "consulta", inicio, fin)

    def _obtener_conflicto(self, unidad: str, inicio: str, fin: str) -> dict | None:
        filas = self._conexion.execute(
            """
            SELECT id, unidad, solicitante, inicio, fin, estado
            FROM reservas
            WHERE unidad = ? AND estado = 'activa'
            ORDER BY id ASC
            """,
            (unidad,),
        ).fetchall()

        for fila in filas:
            if se_superponen(unidad, inicio, fin, unidad, fila["inicio"], fila["fin"]):
                return self._a_diccionario(fila)

        return None

    def crear_reserva(self, unidad: str, solicitante: str, inicio: str, fin: str) -> dict:
        validar_reserva(unidad, solicitante, inicio, fin)

        with self._conexion:
            self._conexion.execute("BEGIN IMMEDIATE")

            conflicto = self._obtener_conflicto(unidad, inicio, fin)
            if conflicto is not None:
                raise ValueError(
                    f"La unidad '{unidad}' ya tiene una reserva activa "
                    "que se superpone con el intervalo solicitado."
                )

            cursor = self._conexion.execute(
                """
                INSERT INTO reservas (unidad, solicitante, inicio, fin, estado)
                VALUES (?, ?, ?, ?, 'activa')
                """,
                (unidad, solicitante.strip(), inicio, fin),
            )
            reserva_id = cursor.lastrowid

        return self.obtener_reserva(reserva_id)

    def cancelar_reserva(self, reserva_id: int) -> dict:
        with self._conexion:
            self._conexion.execute("BEGIN IMMEDIATE")

            fila = self._conexion.execute(
                """
                SELECT id, unidad, solicitante, inicio, fin, estado
                FROM reservas
                WHERE id = ?
                """,
                (reserva_id,),
            ).fetchone()

            if fila is None:
                raise ValueError(f"No existe una reserva con el id {reserva_id}.")
            if fila["estado"] == "cancelada":
                raise ValueError(f"La reserva con id {reserva_id} ya está cancelada.")

            self._conexion.execute(
                "UPDATE reservas SET estado = 'cancelada' WHERE id = ?",
                (reserva_id,),
            )

        reserva_cancelada = self.obtener_reserva(reserva_id)
        if reserva_cancelada is None:
            raise ValueError(f"No existe una reserva con el id {reserva_id}.")
        return reserva_cancelada

    def consultar_disponibilidad(self, unidad: str, inicio: str, fin: str) -> tuple[bool, dict | None]:
        self._validar_intervalo(unidad, inicio, fin)

        with self._conexion:
            self._conexion.execute("BEGIN IMMEDIATE")
            conflicto = self._obtener_conflicto(unidad, inicio, fin)

        return (False, conflicto) if conflicto is not None else (True, None)

    def obtener_reserva(self, reserva_id: int) -> dict | None:
        fila = self._conexion.execute(
            """
            SELECT id, unidad, solicitante, inicio, fin, estado
            FROM reservas
            WHERE id = ?
            """,
            (reserva_id,),
        ).fetchone()

        return None if fila is None else self._a_diccionario(fila)

    def listar_reservas(self) -> list[dict]:
        filas = self._conexion.execute(
            """
            SELECT id, unidad, solicitante, inicio, fin, estado
            FROM reservas
            ORDER BY id ASC
            """
        ).fetchall()

        return [self._a_diccionario(fila) for fila in filas]