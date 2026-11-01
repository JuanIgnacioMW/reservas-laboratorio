import sqlite3

import pytest

from reservas.repositorio import RepositorioReservas

DIA = "2026-10-28"


@pytest.fixture
def repo(tmp_path):
    repositorio = RepositorioReservas(tmp_path / "reservas.db")
    yield repositorio
    repositorio.close()


def test_creacion_valida_persistida(repo):
    reserva = repo.crear_reserva("MIC-01", "Ana", f"{DIA} 10:00", f"{DIA} 11:00")

    assert reserva == {
        "id": 1,
        "unidad": "MIC-01",
        "solicitante": "Ana",
        "inicio": f"{DIA} 10:00",
        "fin": f"{DIA} 11:00",
        "estado": "activa",
    }
    assert repo.obtener_reserva(1) == reserva
    assert repo.listar_reservas() == [reserva]


@pytest.mark.parametrize(
    "inicio, fin",
    [
        ("10:30", "11:30"),  # solapamiento parcial al final
        ("09:30", "10:30"),  # solapamiento parcial al inicio
        ("10:15", "10:45"),  # contenido dentro de la reserva existente
        ("09:30", "11:30"),  # contiene a la reserva existente
        ("10:00", "11:00"),  # idéntico
    ],
)
def test_rechaza_superposicion(repo, inicio, fin):
    repo.crear_reserva("MIC-01", "Ana", f"{DIA} 10:00", f"{DIA} 11:00")

    with pytest.raises(ValueError, match="superpone"):
        repo.crear_reserva("MIC-01", "Luis", f"{DIA} {inicio}", f"{DIA} {fin}")

    assert len(repo.listar_reservas()) == 1


def test_limites_consecutivos_permitidos(repo):
    repo.crear_reserva("MIC-01", "Ana", f"{DIA} 10:00", f"{DIA} 11:00")

    despues = repo.crear_reserva("MIC-01", "Luis", f"{DIA} 11:00", f"{DIA} 12:00")
    antes = repo.crear_reserva("MIC-01", "Eva", f"{DIA} 09:00", f"{DIA} 10:00")

    assert despues["estado"] == "activa"
    assert antes["estado"] == "activa"
    assert len(repo.listar_reservas()) == 3


def test_unidades_distintas_pueden_reservarse_simultaneamente(repo):
    repo.crear_reserva("MIC-01", "Ana", f"{DIA} 10:00", f"{DIA} 11:00")

    reserva = repo.crear_reserva("MIC-02", "Luis", f"{DIA} 10:00", f"{DIA} 11:00")

    assert reserva["unidad"] == "MIC-02"
    assert len(repo.listar_reservas()) == 2


@pytest.mark.parametrize(
    "unidad, solicitante, inicio, fin",
    [
        ("XXX-99", "Ana", f"{DIA} 10:00", f"{DIA} 11:00"),  # unidad desconocida
        ("MIC-01", "", f"{DIA} 10:00", f"{DIA} 11:00"),  # solicitante vacío
        ("MIC-01", "   ", f"{DIA} 10:00", f"{DIA} 11:00"),  # solo espacios
        ("MIC-01", "Ana", "2026-02-30 10:00", f"{DIA} 11:00"),  # inicio con fecha imposible
        ("MIC-01", "Ana", f"{DIA} 10:00", "2026-02-30 11:00"),  # fin con fecha imposible
        ("MIC-01", "Ana", f"{DIA} 25:00", f"{DIA} 11:00"),  # hora imposible
        ("MIC-01", "Ana", "28/10/2026 10:00", "28/10/2026 11:00"),  # formato incorrecto
        ("MIC-01", "Ana", f"{DIA} 11:00", f"{DIA} 11:00"),  # inicio igual al fin
        ("MIC-01", "Ana", f"{DIA} 12:00", f"{DIA} 11:00"),  # inicio posterior al fin
    ],
)
def test_entradas_invalidas_no_se_guardan(repo, unidad, solicitante, inicio, fin):
    with pytest.raises(ValueError):
        repo.crear_reserva(unidad, solicitante, inicio, fin)

    assert repo.listar_reservas() == []


def test_solicitante_se_guarda_sin_espacios_sobrantes(repo):
    reserva = repo.crear_reserva("MIC-01", "  Ana  ", f"{DIA} 10:00", f"{DIA} 11:00")

    assert reserva["solicitante"] == "Ana"


def test_obtener_reserva_inexistente_devuelve_none(repo):
    assert repo.obtener_reserva(999) is None


def _marcar_cancelada(ruta_db, reserva_id):
    # Provisorio: la cancelación todavía no existe en el repositorio (Tarea 3).
    # Se simula editando la base directamente, para comprobar que una reserva
    # cancelada no bloquea el intervalo.
    conexion = sqlite3.connect(ruta_db)
    try:
        with conexion:
            conexion.execute(
                "UPDATE reservas SET estado = 'cancelada' WHERE id = ?",
                (reserva_id,),
            )
    finally:
        conexion.close()


def test_reserva_cancelada_no_bloquea_el_intervalo(tmp_path):
    ruta_db = tmp_path / "reservas.db"

    with RepositorioReservas(ruta_db) as repo:
        original = repo.crear_reserva("MIC-01", "Ana", f"{DIA} 10:00", f"{DIA} 11:00")
        _marcar_cancelada(ruta_db, original["id"])

        nueva = repo.crear_reserva("MIC-01", "Luis", f"{DIA} 10:00", f"{DIA} 11:00")
        reservas = repo.listar_reservas()

    assert nueva["id"] != original["id"]
    assert [r["estado"] for r in reservas] == ["cancelada", "activa"]


def test_reinicio_recupera_reservas_guardadas(tmp_path):
    ruta_db = tmp_path / "reservas.db"

    with RepositorioReservas(ruta_db) as repo_1:
        reserva = repo_1.crear_reserva("MIC-01", "Ana", f"{DIA} 10:00", f"{DIA} 11:00")

    with RepositorioReservas(ruta_db) as repo_2:
        assert repo_2.obtener_reserva(1) == reserva
        assert repo_2.listar_reservas() == [reserva]