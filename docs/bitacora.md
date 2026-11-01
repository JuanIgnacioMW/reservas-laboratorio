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