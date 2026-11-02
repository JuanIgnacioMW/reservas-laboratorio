import argparse
import sys
from pathlib import Path

from reservas.modelo import INVENTARIO
from reservas.repositorio import RepositorioReservas

ROOT = Path(__file__).resolve().parents[2]
DB_POR_DEFECTO = ROOT / "data" / "reservas.db"
INVENTARIO_POR_DEFECTO = ROOT / "data" / "inventario.json"


class ErrorCLI(Exception):
    """Representa un error de uso o de validación del CLI."""


def _traducir_mensaje_error(mensaje: str) -> str:
    texto = mensaje
    reemplazos = {
        "the following arguments are required: ": "faltan los argumentos: ",
        "unrecognized arguments: ": "argumentos no reconocidos: ",
        "expected one argument": "se esperaba un argumento",
        "invalid int value": "valor entero inválido",
        "invalid choice": "opción inválida",
        "argument ": "argumento ",
        "not allowed": "no permitido",
        "is required": "es requerido",
    }
    for original, traduccion in reemplazos.items():
        texto = texto.replace(original, traduccion)
    return texto


class ParserConArgumentos(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ErrorCLI(_traducir_mensaje_error(message))


def _ruta_db_por_defecto() -> Path:
    return DB_POR_DEFECTO


def _ruta_inventario_por_defecto() -> Path:
    return INVENTARIO_POR_DEFECTO


def _crear_parser() -> argparse.ArgumentParser:
    parser_base = argparse.ArgumentParser(add_help=False)
    parser_base.add_argument(
        "--db",
        default=str(_ruta_db_por_defecto()),
        help="Ruta del archivo SQLite de reservas.",
    )

    parser = ParserConArgumentos(
        description="Administración de reservas del laboratorio.",
    )
    parser.add_argument(
        "--db",
        default=str(_ruta_db_por_defecto()),
        help="Ruta del archivo SQLite de reservas.",
    )
    subparsers = parser.add_subparsers(dest="comando", required=True)

    subparsers.add_parser("unidades", help="Lista el inventario del laboratorio.")

    disponibilidad = subparsers.add_parser(
        "disponibilidad",
        parents=[parser_base],
        help="Consulta si una unidad está disponible en un intervalo.",
    )
    disponibilidad.add_argument("unidad")
    disponibilidad.add_argument("inicio")
    disponibilidad.add_argument("fin")

    reservar = subparsers.add_parser(
        "reservar",
        parents=[parser_base],
        help="Crea una reserva para una unidad.",
    )
    reservar.add_argument("unidad")
    reservar.add_argument("solicitante")
    reservar.add_argument("inicio")
    reservar.add_argument("fin")

    cancelar = subparsers.add_parser(
        "cancelar",
        parents=[parser_base],
        help="Cancela una reserva existente.",
    )
    cancelar.add_argument("id_reserva", type=int)

    subparsers.add_parser("listar", parents=[parser_base], help="Lista reservas activas y canceladas.")

    reiniciar = subparsers.add_parser(
        "reiniciar-datos",
        parents=[parser_base],
        help="Borra todas las reservas creadas.",
    )
    reiniciar.add_argument(
        "--confirmar",
        action="store_true",
        help="Requiere confirmación explícita para borrar todas las reservas.",
    )

    return parser


def _imprimir_reserva(reserva: dict) -> None:
    print(
        f"{reserva['id']} | {reserva['unidad']} | {reserva['solicitante']} | "
        f"{reserva['inicio']} | {reserva['fin']} | {reserva['estado']}"
    )


def _comando_unidades(args: argparse.Namespace) -> int:
    for unidad, equipo in INVENTARIO.items():
        print(f"{unidad} | {equipo}")
    return 0


def _comando_disponibilidad(args: argparse.Namespace) -> int:
    with RepositorioReservas(args.db) as repo:
        disponible, conflicto = repo.consultar_disponibilidad(args.unidad, args.inicio, args.fin)

    if disponible:
        print("Disponible.")
        return 0

    if conflicto is None:
        print("No disponible.")
        return 1

    print(
        f"No disponible: la unidad '{conflicto['unidad']}' ya tiene una reserva activa "
        f"en el intervalo solicitado (reserva {conflicto['id']})."
    )
    return 1


def _comando_reservar(args: argparse.Namespace) -> int:
    with RepositorioReservas(args.db) as repo:
        reserva = repo.crear_reserva(args.unidad, args.solicitante, args.inicio, args.fin)

    print(f"Reserva creada: {reserva['id']}")
    _imprimir_reserva(reserva)
    return 0


def _comando_cancelar(args: argparse.Namespace) -> int:
    with RepositorioReservas(args.db) as repo:
        reserva = repo.cancelar_reserva(args.id_reserva)

    print(f"Reserva cancelada: {reserva['id']}")
    _imprimir_reserva(reserva)
    return 0


def _comando_listar(args: argparse.Namespace) -> int:
    with RepositorioReservas(args.db) as repo:
        reservas = repo.listar_reservas()

    if not reservas:
        print("No hay reservas.")
        return 0

    for reserva in reservas:
        _imprimir_reserva(reserva)
    return 0


def _comando_reiniciar_datos(args: argparse.Namespace) -> int:
    if not args.confirmar:
        print(
            "No se borraron los datos: se requiere --confirmar para reiniciar el almacenamiento.",
            file=sys.stderr,
        )
        return 1

    with RepositorioReservas(args.db) as repo:
        repo.reiniciar_datos()

    print("Se borraron todas las reservas.")
    return 0


def main(argv: list[str] | None = None) -> int:
    argumentos = list(sys.argv[1:] if argv is None else argv)
    parser = _crear_parser()
    base_db = str(_ruta_db_por_defecto())

    try:
        if "--db" in argumentos:
            indice = argumentos.index("--db")
            if indice + 1 >= len(argumentos):
                raise ErrorCLI("Falta el valor para la opción --db.")
            base_db = argumentos[indice + 1]
            argumentos = argumentos[:indice] + argumentos[indice + 2 :]

        args = parser.parse_args(argumentos)
        args.db = base_db

        if args.comando == "unidades":
            return _comando_unidades(args)
        if args.comando == "disponibilidad":
            return _comando_disponibilidad(args)
        if args.comando == "reservar":
            return _comando_reservar(args)
        if args.comando == "cancelar":
            return _comando_cancelar(args)
        if args.comando == "listar":
            return _comando_listar(args)
        if args.comando == "reiniciar-datos":
            return _comando_reiniciar_datos(args)
        raise ErrorCLI("Comando no reconocido.")
    except ErrorCLI as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except FileNotFoundError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
