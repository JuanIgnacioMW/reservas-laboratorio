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

    def crear_reserva(self, unidad: str, solicitante: str, inicio: str, fin: str) -> dict:
        validar_reserva(unidad, solicitante, inicio, fin)

        with self._conexion:
            # BEGIN IMMEDIATE abre la transacción y toma el bloqueo de escritura
            # antes de leer, de modo que el chequeo de superposición y el INSERT
            # ocurren dentro de la misma transacción.
            self._conexion.execute("BEGIN IMMEDIATE")

            filas = self._conexion.execute(
                """
                SELECT inicio, fin
                FROM reservas
                WHERE unidad = ? AND estado = 'activa'
                """,
                (unidad,),
            ).fetchall()

            for fila in filas:
                if se_superponen(unidad, inicio, fin, unidad, fila["inicio"], fila["fin"]):
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