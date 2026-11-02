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


def test_cancelar_reserva_conserva_id_y_datos(repo):
    reserva = repo.crear_reserva("MIC-01", "Ana", f"{DIA} 10:00", f"{DIA} 11:00")

    cancelada = repo.cancelar_reserva(reserva["id"])

    assert cancelada["id"] == reserva["id"]
    assert cancelada["unidad"] == reserva["unidad"]
    assert cancelada["solicitante"] == reserva["solicitante"]
    assert cancelada["inicio"] == reserva["inicio"]
    assert cancelada["fin"] == reserva["fin"]
    assert cancelada["estado"] == "cancelada"
    assert repo.obtener_reserva(reserva["id"]) == cancelada
    assert repo.listar_reservas() == [cancelada]


def test_cancelar_reserva_libera_el_intervalo_y_permite_rereservar(repo):
    original = repo.crear_reserva("MIC-01", "Ana", f"{DIA} 10:00", f"{DIA} 11:00")

    repo.cancelar_reserva(original["id"])
    nueva = repo.crear_reserva("MIC-01", "Luis", f"{DIA} 10:00", f"{DIA} 11:00")
    reservas = repo.listar_reservas()

    assert nueva["id"] != original["id"]
    assert nueva["estado"] == "activa"
    assert [r["estado"] for r in reservas] == ["cancelada", "activa"]


def test_cancelar_reserva_inexistente_o_ya_cancelada_falla(repo):
    with pytest.raises(ValueError, match="No existe"):
        repo.cancelar_reserva(999)

    reserva = repo.crear_reserva("MIC-01", "Ana", f"{DIA} 10:00", f"{DIA} 11:00")
    repo.cancelar_reserva(reserva["id"])

    with pytest.raises(ValueError, match="cancelada"):
        repo.cancelar_reserva(reserva["id"])


def test_consultar_disponibilidad_coincide_con_crear_reserva(repo):
    original = repo.crear_reserva("MIC-01", "Ana", f"{DIA} 10:00", f"{DIA} 11:00")

    assert repo.consultar_disponibilidad("MIC-01", f"{DIA} 10:30", f"{DIA} 11:30") == (
        False,
        original,
    )
    with pytest.raises(ValueError, match="superpone"):
        repo.crear_reserva("MIC-01", "Luis", f"{DIA} 10:30", f"{DIA} 11:30")

    assert repo.consultar_disponibilidad("MIC-01", f"{DIA} 11:00", f"{DIA} 12:00") == (
        True,
        None,
    )
    reserva_consecutiva = repo.crear_reserva("MIC-01", "Luis", f"{DIA} 11:00", f"{DIA} 12:00")
    assert reserva_consecutiva["estado"] == "activa"

    assert repo.consultar_disponibilidad("MIC-02", f"{DIA} 10:00", f"{DIA} 11:00") == (
        True,
        None,
    )


@pytest.mark.parametrize(
    "unidad, inicio, fin",
    [
        ("XXX-99", f"{DIA} 10:00", f"{DIA} 11:00"),
        ("MIC-01", "2026-02-30 10:00", f"{DIA} 11:00"),
        ("MIC-01", f"{DIA} 11:00", f"{DIA} 11:00"),
    ],
)
def test_consultar_disponibilidad_rechaza_entradas_invalidas(repo, unidad, inicio, fin):
    with pytest.raises(ValueError):
        repo.consultar_disponibilidad(unidad, inicio, fin)


def test_reinicio_recupera_reservas_activas_y_canceladas(tmp_path):
    ruta_db = tmp_path / "reservas.db"

    with RepositorioReservas(ruta_db) as repo_1:
        activa = repo_1.crear_reserva("MIC-01", "Ana", f"{DIA} 10:00", f"{DIA} 11:00")
        otra = repo_1.crear_reserva("MIC-02", "Luis", f"{DIA} 10:00", f"{DIA} 11:00")
        cancelada = repo_1.cancelar_reserva(otra["id"])

    with RepositorioReservas(ruta_db) as repo_2:
        assert repo_2.obtener_reserva(activa["id"]) == activa
        assert repo_2.obtener_reserva(cancelada["id"]) == cancelada
        assert repo_2.listar_reservas() == [activa, cancelada]