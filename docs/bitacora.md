# Bitácora de trabajo

## 2026-10-28: Preparación del entorno

**Entorno**
- Editor: Visual Studio Code, versión
- Agente: GitHub Copilot, modo Agent, integrado en VS Code
- Modelo: [COPILOT, balance auto]
- Plan de la cuenta: gratuito
- Python: [3.13.2]
- Carpeta de trabajo: solo la carpeta del repositorio, abierta de forma aislada

**Comprobaciones realizadas (ejecutadas por mí)**
- `git status` en la carpeta del repo: rama main, árbol limpio.
- `git remote -v`: apunta únicamente a este repositorio.
- Prueba del agente: le pedí crear un archivo de prueba. El archivo se creó y
  quedó pendiente de revisión (Keep/Undo). Lo descarté con Undo y `git status`
  volvió a mostrar el árbol limpio.
- Prueba de comandos: le pedí ejecutar `python --version`. Copilot pidió
  autorización antes de ejecutarlo y yo la concedí.

**Controles previstos**
- Aprobación manual de cada comando de terminal.
- Revisión de los cambios en Source Control y con `git diff` antes de commitear.
- Los commits los hago yo.

**Decisiones**
- Lenguaje: Python. Almacenamiento: SQLite. Interfaz: consola.
- Especificación inicial: docs/especificacion.md.
- 
 - En tarea 1 delegada al agente
 - **Verificación real:** al ejecutar `pytest` (Python 3.13.2, pytest 9.2.0) falló la
  recolección con ModuleNotFoundError: No module named 'reservas'.
- **Causa:** pytest no tenía `src` en el path.
- **Corrección:** [hecha por mí] agregando pyproject.toml con
  `pythonpath = ["src"]`.
- **Resultado tras corregir:** [completar con la salida real de pytest].
- Ejecucion en la terminal:
================================ test session starts ================================
platform win32 -- Python 3.13.2, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\Flia Meza\Desktop\Reservas-Laboratorio\reservas-laboratorio
collected 0 items / 1 error                                                          

====================================== ERRORS =======================================
_______________________ ERROR collecting tests/test_modelo.py _______________________
ImportError while importing test module 'C:\Users\Flia Meza\Desktop\Reservas-Laboratorio\reservas-laboratorio\tests\test_modelo.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
..\..\..\AppData\Local\Programs\Python\Python313\Lib\importlib\__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_modelo.py:3: in <module>
    from reservas.modelo import INVENTARIO, se_superponen, validar_reserva
E   ModuleNotFoundError: No module named 'reservas'
============================== short test summary info ==============================
ERROR tests/test_modelo.py
!!!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!!!!
================================= 1 error in 0.16s ==================================
PS C:\Users\Flia Meza\Desktop\Reservas-Laboratorio\reservas-laboratorio> pytest
================================ test session starts ================================
platform win32 -- Python 3.13.2, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\Flia Meza\Desktop\Reservas-Laboratorio\reservas-laboratorio
configfile: pyproject.toml
testpaths: tests
collected 12 items                                                                   

tests\test_modelo.py ............                                              [100%]

================================ 12 passed in 0.06s =================================

Commit de la tarea 1

PS C:\Users\Flia Meza\Desktop\Reservas-Laboratorio\reservas-laboratorio> git log --oneline
7ce003b (HEAD -> main, origin/main, origin/HEAD) Tarea 1: modelo de datos, validaciones y pruebas
5ca2c77 Se agrega instrucciones del agente con regla de turnos consecutivos
c3efc34 Agrega bitácora con la validación del entorno
401d4cb Agrega .gitignore para Python
979571a Agrega especificación inicial.md
cd152c6 Initial commit


(episodio 2)

## Episodio 2: persistencia con SQLite

- **Objetivo y requisito:** R11 (parcial) y R12 de `docs/especificacion.md`: guardar reservas
  con su estado y recuperarlas al reiniciar. Sin cancelación, disponibilidad ni consola
  (eso queda para la Tarea 3).
- **Contexto suministrado:** `docs/especificacion.md` y `.github/copilot-instructions.md`,
  con la sección "Persistencia" agregada y subida antes de delegar. Quedó fuera de contexto
  cualquier dato real: los solicitantes son ficticios.
- **Extracto de la instrucción:** "Tarea 2: persistencia con SQLite. Sin cancelación,
  disponibilidad ni consola todavía. [...] No modifiques los archivos de la Tarea 1 salvo
  que sea imprescindible, y avisame si lo hacés. Ejecutá pytest y mostrame el resultado real."
- **Acción del agente:** creó `src/reservas/repositorio.py` y `tests/test_repositorio.py`
  (6 pruebas). Al terminar informó: que pasaron las pruebas pregunto si queria mantener.
  Comandos que aprobé:
                      ======================== test session starts =========================
platform win32 -- Python 3.13.2, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\Flia Meza\Desktop\Reservas-Laboratorio\reservas-laboratorio
configfile: pyproject.toml
testpaths: tests
collected 33 items                                                    

tests\test_modelo.py ............                               [ 36%]
tests\test_repositorio.py .....................                 [100%]

========================= 33 passed in 0.36s =========================

Mutación: quité AND estado = 'activa' del SELECT en crear_reserva.
Resultado: pytest → 1 failed, 32 passed (Python 3.13.2, pytest 9.2.0); falló test_reserva_cancelada_no_bloquea_el_intervalo con ValueError.
Conclusión: el test nuevo cubre un hueco de la versión del agente. Tras revertir: 33 passed.

 pytest 
===================================== test session starts ======================================
platform win32 -- Python 3.13.2, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\Flia Meza\Desktop\Reservas-Laboratorio\reservas-laboratorio
configfile: pyproject.toml
testpaths: tests
collected 33 items                                                                              

tests\test_modelo.py ............                                                         [ 36%]
tests\test_repositorio.py ...................F.                                           [100%]

=========================================== FAILURES ===========================================
________________________ test_reserva_cancelada_no_bloquea_el_intervalo ________________________

tmp_path = WindowsPath('C:/Users/Flia Meza/AppData/Local/Temp/pytest-of-Flia Meza/pytest-3/test_reserva_cancelada_no_bloq0')

    def test_reserva_cancelada_no_bloquea_el_intervalo(tmp_path):
        ruta_db = tmp_path / "reservas.db"
    
        with RepositorioReservas(ruta_db) as repo:
            original = repo.crear_reserva("MIC-01", "Ana", f"{DIA} 10:00", f"{DIA} 11:00")
            _marcar_cancelada(ruta_db, original["id"])
    
>           nueva = repo.crear_reserva("MIC-01", "Luis", f"{DIA} 10:00", f"{DIA} 11:00")
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_repositorio.py:124: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <reservas.repositorio.RepositorioReservas object at 0x0000021F0D09E3F0>, unidad = 'MIC-01'
solicitante = 'Luis', inicio = '2026-10-28 10:00', fin = '2026-10-28 11:00'

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
                WHERE unidad = ?
                """,
                (unidad,),
            ).fetchall()
    
            for fila in filas:
                if se_superponen(unidad, inicio, fin, unidad, fila["inicio"], fila["fin"]):
>                   raise ValueError(
                        f"La unidad '{unidad}' ya tiene una reserva activa "
                        "que se superpone con el intervalo solicitado."
                    )
E                   ValueError: La unidad 'MIC-01' ya tiene una reserva activa que se superpone con el intervalo solicitado.

src\reservas\repositorio.py:68: ValueError
=================================== short test summary info ====================================
FAILED tests/test_repositorio.py::test_reserva_cancelada_no_bloquea_el_intervalo - ValueError: La unidad 'MIC-01' ya tiene una reserva activa que se superpone con el intervalo...
================================= 1 failed, 32 passed in 0.42s =================================
PS C:\Users\Flia Meza\Desktop\Reservas-Laboratorio\reservas-laboratorio>  pytest
===================================== test session starts ======================================
platform win32 -- Python 3.13.2, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\Flia Meza\Desktop\Reservas-Laboratorio\reservas-laboratorio
configfile: pyproject.toml
testpaths: tests
collected 33 items                                                                              

tests\test_modelo.py ............                                                         [ 36%]
tests\test_repositorio.py .....................                                           [100%]

====================================== 33 passed in 0.34s ====================================== .
  
El chat mostró `copilot-instructions.md` entre las referencias usadas, cuanbdo esta desarrollando el codigo.
- **Verificación humana (ejecutada por mí):**
  - `git status`: solo los dos archivos nuevos sin seguimiento; `git diff --stat` vacío, es decir, no modificó archivos de la Tarea 1.
  - `pytest` (Python 3.13.2, pytest 9.2.0) sobre la versión del agente: 18 passed, lo que coincide con lo informado por el agente.
  - Revisión del código contra una lista de control: SQL con parámetros, superposición solo contra reservas activas de la misma unidad, `CHECK` en el estado, pruebas con  `tmp_path`.
- **Hallazgos de la revisión:**
  1. La transacción no abarcaba el `SELECT`: en `sqlite3` la transacción implícita se abre recién en el `INSERT`, así que el chequeo de superposición y el guardado no eran atómicos, a pesar de que el pedido decía "en una misma transacción".
  2. La conexión no tenía forma de cerrarse.
  3. Ninguna prueba cubría que una reserva cancelada no bloquea el intervalo: quitar el filtro `estado = 'activa'` no habría roto ningún test.
- **Decisión: corregir.** Acepté la estructura y el enfoque del agente y corregí lo anterior: agregué `BEGIN IMMEDIATE` antes del `SELECT`, `close()` y soporte para `with`, y
  amplié las pruebas del repositorio de 6 a 21 (más patrones de superposición, consecutivos por ambos lados, más entradas inválidas, `strip` del solicitante, reserva inexistente, reserva cancelada que no bloquea y reinicio). Estas mejoras las redacté con ayuda de un asistente de chat, y las revisé, ejecuté y acepté yo antes de commitear.
- **Evidencia:**
  - `pytest`: 33 passed (12 de la Tarea 1 y 21 del repositorio).
  - Prueba de mutación: quité `AND estado = 'activa'` del `SELECT` de `crear_reserva` →
    1 failed, 32 passed; falló `test_reserva_cancelada_no_bloquea_el_intervalo` con
    `ValueError`. Tras revertir el cambio: [completar: 33 passed].
  - Comprobación manual del formato: `validar_reserva('MIC-01', 'Ana', '2026-10-28 9:00', '2026-10-28 10:00')` → `ValueError: La fecha debe tener el formato AAAA-MM-DD HH:MM.`
    No se agregó test automático para este caso; queda como comprobación manual.
  - `dir data`: solo `inventario.json`, así que ningún test usó la base real.
  - Commit: [completar con el hash de `git log --oneline`]. Archivos:
    `src/reservas/repositorio.py`, `tests/test_repositorio.py`.
- **Limitaciones conocidas:**
  - `BEGIN IMMEDIATE` está justificado por la revisión del código, pero ninguna prueba lo
    comprueba con dos conexiones simultáneas (concurrencia fuera de alcance). No probé qué
    pasa al quitarlo.
  - La persistencia de reservas canceladas tras un reinicio se verificará en la Tarea 3;
    en esta tarea la cancelación se simula en una prueba editando la base directamente.
  - Los tests no cierran el caso de hora sin cero inicial de forma automática.

git log --oneline
b2d83f0 (HEAD -> main, origin/main, origin/HEAD) Tarea 2: se agrega hash de los commit de este episodio 2
bf179ee Tarea 2: persistencia con SQLite; corrige transacción, agrega close() y amplía pruebas tras revisión
dfecc17 Tarea 2 (agente): persistencia con SQLite y pruebas, versión original de Copilot
a564004 Ignora la base de datos local en .gitignore
87ce210 Se agrega la persitencia en el archivo copilot-intructions
7ce003b Tarea 1: modelo de datos, validaciones y pruebas
5ca2c77 Se agrega instrucciones del agente con regla de turnos consecutivos
c3efc34 Agrega bitácora con la validación del entorno
401d4cb Agrega .gitignore para Python
979571a Agrega especificación inicial.md
cd152c6 Initial commit


