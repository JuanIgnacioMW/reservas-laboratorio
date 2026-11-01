import pytest

from reservas.repositorio import RepositorioReservas


def test_creacion_valida_persistida(tmp_path):
    ruta_db = tmp_path / "reservas.db"
    repo = RepositorioReservas(ruta_db)

    reserva = repo.crear_reserva(
        "MIC-01",
        "Ana",
        "2026-10-28 10:00",
        "2026-10-28 11:00",
    )

    assert reserva == {
        "id": 1,
        "unidad": "MIC-01",
        "solicitante": "Ana",
        "inicio": "2026-10-28 10:00",
        "fin": "2026-10-28 11:00",
        "estado": "activa",
    }
    assert repo.obtener_reserva(1) == reserva
    assert repo.listar_reservas() == [reserva]


def test_rechaza_superposicion(tmp_path):
    repo = RepositorioReservas(tmp_path / "reservas.db")
    repo.crear_reserva("MIC-01", "Ana", "2026-10-28 10:00", "2026-10-28 11:00")

    with pytest.raises(ValueError, match="superpone"):
        repo.crear_reserva(
            "MIC-01",
            "Luis",
            "2026-10-28 10:30",
            "2026-10-28 11:30",
        )

    assert len(repo.listar_reservas()) == 1


def test_limite_consecutivo_permitido(tmp_path):
    repo = RepositorioReservas(tmp_path / "reservas.db")
    repo.crear_reserva("MIC-01", "Ana", "2026-10-28 10:00", "2026-10-28 11:00")

    reserva = repo.crear_reserva(
        "MIC-01",
        "Luis",
        "2026-10-28 11:00",
        "2026-10-28 12:00",
    )

    assert reserva["estado"] == "activa"
    assert len(repo.listar_reservas()) == 2


def test_unidades_distintas_pueden_reservarse_simultaneamente(tmp_path):
    repo = RepositorioReservas(tmp_path / "reservas.db")
    repo.crear_reserva("MIC-01", "Ana", "2026-10-28 10:00", "2026-10-28 11:00")

    reserva = repo.crear_reserva(
        "MIC-02",
        "Luis",
        "2026-10-28 10:00",
        "2026-10-28 11:00",
    )

    assert reserva["unidad"] == "MIC-02"
    assert len(repo.listar_reservas()) == 2


def test_entradas_invalidas_no_se_guardan(tmp_path):
    repo = RepositorioReservas(tmp_path / "reservas.db")

    with pytest.raises(ValueError):
        repo.crear_reserva("XXX-99", "Ana", "2026-10-28 10:00", "2026-10-28 11:00")
    with pytest.raises(ValueError):
        repo.crear_reserva("MIC-01", "   ", "2026-10-28 10:00", "2026-10-28 11:00")
    with pytest.raises(ValueError):
        repo.crear_reserva("MIC-01", "Ana", "2026-02-30 10:00", "2026-10-28 11:00")
    with pytest.raises(ValueError):
        repo.crear_reserva("MIC-01", "Ana", "2026-10-28 11:00", "2026-10-28 11:00")

    assert repo.listar_reservas() == []


def test_reinicio_recupera_reservas_guardadas(tmp_path):
    ruta_db = tmp_path / "reservas.db"
    repo_1 = RepositorioReservas(ruta_db)
    reserva = repo_1.crear_reserva(
        "MIC-01",
        "Ana",
        "2026-10-28 10:00",
        "2026-10-28 11:00",
    )

    repo_2 = RepositorioReservas(ruta_db)

    assert repo_2.obtener_reserva(1) == reserva
    assert repo_2.listar_reservas() == [reserva]
