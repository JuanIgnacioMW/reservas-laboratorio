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