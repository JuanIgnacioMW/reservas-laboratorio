import pytest

from reservas.modelo import INVENTARIO, se_superponen, validar_reserva


@pytest.mark.parametrize(
    ("unidad", "solicitante", "inicio", "fin"),
    [
        ("XXX-99", "Ana", "2026-10-28 10:00", "2026-10-28 11:00"),
        ("MIC-01", "", "2026-10-28 10:00", "2026-10-28 11:00"),
        ("MIC-01", "   ", "2026-10-28 10:00", "2026-10-28 11:00"),
        ("MIC-01", "Ana", "2026-02-30 10:00", "2026-10-28 11:00"),
        ("MIC-01", "Ana", "28-10-2026 10:00", "2026-10-28 11:00"),
        ("MIC-01", "Ana", "2026-1-28 10:00", "2026-10-28 11:00"),
        ("MIC-01", "Ana", "2026-10-28 10:00", "2026-10-28 10:00"),
        ("MIC-01", "Ana", "2026-10-28 12:00", "2026-10-28 11:00"),
    ],
)
def test_validar_reserva_rechaza_datos_invalidos(
    unidad: str, solicitante: str, inicio: str, fin: str
) -> None:
    with pytest.raises(ValueError):
        validar_reserva(unidad, solicitante, inicio, fin)


def test_inventario_cargado_tiene_las_cinco_unidades() -> None:
    assert INVENTARIO == {
        "MIC-01": "Microscopio digital",
        "MIC-02": "Microscopio digital",
        "OSC-01": "Osciloscopio",
        "MUL-01": "Multímetro",
        "FUE-01": "Fuente de alimentación",
    }


def test_se_superponen_intervalos_solapados_de_la_misma_unidad() -> None:
    assert se_superponen(
        "MIC-01",
        "2026-10-28 10:00",
        "2026-10-28 11:00",
        "MIC-01",
        "2026-10-28 10:30",
        "2026-10-28 11:30",
    )


def test_no_se_superponen_intervalos_consecutivos() -> None:
    assert not se_superponen(
        "MIC-01",
        "2026-10-28 10:00",
        "2026-10-28 11:00",
        "MIC-01",
        "2026-10-28 11:00",
        "2026-10-28 12:00",
    )


def test_unidades_distintas_pueden_usarse_simultaneamente() -> None:
    assert not se_superponen(
        "MIC-01",
        "2026-10-28 10:00",
        "2026-10-28 11:00",
        "MIC-02",
        "2026-10-28 10:00",
        "2026-10-28 11:00",
    )
    validar_reserva("MIC-01", "Ana", "2026-10-28 10:00", "2026-10-28 11:00")
    validar_reserva("MIC-02", "Luis", "2026-10-28 10:00", "2026-10-28 11:00")
