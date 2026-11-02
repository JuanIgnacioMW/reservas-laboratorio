from reservas.cli import main
from reservas.repositorio import RepositorioReservas

DIA = "2026-10-28"


def test_cli_reservar_y_listar(tmp_path, capsys):
    db = tmp_path / "reservas.db"

    codigo = main(["--db", str(db), "reservar", "MIC-01", "Ana", f"{DIA} 10:00", f"{DIA} 11:00"])
    assert codigo == 0
    salida = capsys.readouterr()
    assert "Reserva creada" in salida.out
    assert "MIC-01" in salida.out

    codigo = main(["--db", str(db), "listar"])
    assert codigo == 0
    salida = capsys.readouterr()
    assert "MIC-01" in salida.out
    assert "Ana" in salida.out
    assert "activa" in salida.out


def test_cli_rechaza_superposicion(tmp_path, capsys):
    db = tmp_path / "reservas.db"
    codigo = main(["--db", str(db), "reservar", "MIC-01", "Ana", f"{DIA} 10:00", f"{DIA} 11:00"])
    assert codigo == 0

    codigo = main(["--db", str(db), "reservar", "MIC-01", "Luis", f"{DIA} 10:30", f"{DIA} 11:30"])
    assert codigo == 1
    salida = capsys.readouterr()
    assert "superpone" in salida.err.lower()


def test_cli_permite_turno_consecutivo(tmp_path, capsys):
    db = tmp_path / "reservas.db"
    codigo = main(["--db", str(db), "reservar", "MIC-01", "Ana", f"{DIA} 10:00", f"{DIA} 11:00"])
    assert codigo == 0

    codigo = main(["--db", str(db), "reservar", "MIC-01", "Luis", f"{DIA} 11:00", f"{DIA} 12:00"])
    assert codigo == 0
    salida = capsys.readouterr()
    assert "Reserva creada" in salida.out


def test_cli_cancelar_libera_disponibilidad(tmp_path, capsys):
    db = tmp_path / "reservas.db"
    codigo = main(["--db", str(db), "reservar", "MIC-01", "Ana", f"{DIA} 10:00", f"{DIA} 11:00"])
    assert codigo == 0

    codigo = main(["--db", str(db), "cancelar", "1"])
    assert codigo == 0
    salida = capsys.readouterr()
    assert "cancelada" in salida.out.lower()

    codigo = main(["--db", str(db), "disponibilidad", "MIC-01", f"{DIA} 10:00", f"{DIA} 11:00"])
    assert codigo == 0
    salida = capsys.readouterr()
    assert "Disponible" in salida.out


def test_cli_rechaza_entradas_invalidas(tmp_path, capsys):
    db = tmp_path / "reservas.db"

    codigo = main(["--db", str(db), "reservar", "MIC-99", "Ana", f"{DIA} 10:00", f"{DIA} 11:00"])
    assert codigo == 1
    salida = capsys.readouterr()
    assert "no existe" in salida.err.lower()

    codigo = main(["--db", str(db), "reservar", "MIC-01", "   ", f"{DIA} 10:00", f"{DIA} 11:00"])
    assert codigo == 1
    salida = capsys.readouterr()
    assert "solicitante" in salida.err.lower()


def test_cli_reiniciar_datos_requiere_confirmacion(tmp_path, capsys):
    db = tmp_path / "reservas.db"
    codigo = main(["--db", str(db), "reservar", "MIC-01", "Ana", f"{DIA} 10:00", f"{DIA} 11:00"])
    assert codigo == 0

    codigo = main(["--db", str(db), "reiniciar-datos"])
    assert codigo == 1
    salida = capsys.readouterr()
    assert "--confirmar" in salida.err

    with RepositorioReservas(db) as repo:
        assert len(repo.listar_reservas()) == 1


def test_cli_reiniciar_datos_con_confirmacion_borra_todo(tmp_path, capsys):
    db = tmp_path / "reservas.db"
    codigo = main(["--db", str(db), "reservar", "MIC-01", "Ana", f"{DIA} 10:00", f"{DIA} 11:00"])
    assert codigo == 0

    codigo = main(["--db", str(db), "reiniciar-datos", "--confirmar"])
    assert codigo == 0
    salida = capsys.readouterr()
    assert "borraron" in salida.out.lower()

    with RepositorioReservas(db) as repo:
        assert repo.listar_reservas() == []
