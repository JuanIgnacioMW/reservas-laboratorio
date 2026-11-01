import sqlite3
from pathlib import Path

from reservas.modelo import se_superponen, validar_reserva


class RepositorioReservas:
    def __init__(self, ruta_archivo: str | Path):
        self.ruta_archivo = Path(ruta_archivo)
        self.ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
        self._conexion = sqlite3.connect(self.ruta_archivo)
        self._conexion.row_factory = sqlite3.Row
        self._crear_tabla()

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

    def crear_reserva(self, unidad: str, solicitante: str, inicio: str, fin: str) -> dict:
        validar_reserva(unidad, solicitante, inicio, fin)

        with self._conexion:
            filas = self._conexion.execute(
                """
                SELECT inicio, fin
                FROM reservas
                WHERE unidad = ? AND estado = 'activa'
                """,
                (unidad,),
            ).fetchall()

            for fila in filas:
                if se_superponen(
                    unidad,
                    inicio,
                    fin,
                    unidad,
                    fila["inicio"],
                    fila["fin"],
                ):
                    raise ValueError(
                        f"La unidad '{unidad}' ya tiene una reserva activa que se superpone con el intervalo solicitado."
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

        if fila is None:
            return None

        return {key: fila[key] for key in ("id", "unidad", "solicitante", "inicio", "fin", "estado")}

    def listar_reservas(self) -> list[dict]:
        filas = self._conexion.execute(
            """
            SELECT id, unidad, solicitante, inicio, fin, estado
            FROM reservas
            ORDER BY id ASC
            """
        ).fetchall()

        return [
            {key: fila[key] for key in ("id", "unidad", "solicitante", "inicio", "fin", "estado")}
            for fila in filas
        ]
