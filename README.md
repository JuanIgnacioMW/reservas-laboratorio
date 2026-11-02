# Sistema de reservas de laboratorio

Trabajo práctico "Challenge IA": sistema de reservas de equipos de laboratorio, en consola, desarrollado con un agente de programación (GitHub Copilot en modo Agent, dentro de VS Code).

Secciones: [1. Especificación](#1-especificación-breve) ·
[2. Solución](#2-solución) · [3. Preparación del agente](#3-preparación-del-agente) ·
[4. Registro de decisiones y delegación](#4-registro-de-decisiones-y-delegación)

## 1. Especificación breve

- **Problema:** la coordinación de un laboratorio registra pedidos en mensajes y una planilla; a veces se confirma la misma unidad en horarios superpuestos y otras veces una cancelación sigue bloqueando el horario.
- **Alcance:** consultar disponibilidad por unidad e intervalo, reservar, cancelar sin perder el historial y persistir los datos entre reinicios. Una unidad por reserva. Interfaz de consola.
- **Reglas principales:** una reserva activa ocupa el intervalo y una cancelada no bloquea; se valida unidad conocida, solicitante no vacío ni solo espacios, fechas válidas y inicio estrictamente anterior al fin; se rechazan superposiciones de la misma unidad, se permiten
  límites consecutivos (10:00-11:00 y 11:00-12:00) y reservas simultáneas de unidades distintas; la disponibilidad usa las mismas reglas que la reserva.
- **Supuestos:** hora local sin zonas horarias; formato `AAAA-MM-DD HH:MM`; se permiten fechas pasadas (para que las pruebas no dependan del reloj); sin límite de duración ni de anticipación; los solicitantes son ficticios.
- **Especificación completa, requisitos y criterios de aceptación:**
  [docs/especificacion.md](docs/especificacion.md). La versión inicial está en el commit `979571a` y los cambios posteriores son recuperables con `git log`.

## 2. Solución

### Estructura

```
src/reservas/modelo.py        validaciones, inventario y regla de superposición
src/reservas/repositorio.py   persistencia en SQLite, cancelación y disponibilidad
src/reservas/cli.py           interfaz de consola (argparse)
src/reservas/__main__.py      permite ejecutar python -m reservas
tests/                        pruebas automáticas (pytest)
data/inventario.json          inventario inicial (5 unidades)
docs/                         especificación, bitácora y evidencia
```

### Decisiones técnicas

- Python con SQLite (módulo `sqlite3` de la biblioteca estándar); única dependencia de desarrollo: `pytest`.
- La consola y la consulta de disponibilidad reutilizan las mismas funciones de validación y superposición que la creación de reservas, para que no puedan discrepar.
- Intervalos semiabiertos: incluyen el inicio y excluyen el fin.

### Requisitos previos y versiones

Python 3.10 o superior. Probado con Python 3.13.2, pip 24.3.1 y pytest 9.2.0, en Windows con PowerShell.

### Instalación

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass   # solo para esta terminal
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

En cada terminal nueva hay que volver a activar el entorno; si no, `python -m reservas` falla
con `No module named reservas`.

### Uso

```powershell
python -m reservas unidades
python -m reservas disponibilidad MIC-01 "2026-10-28 11:00" "2026-10-28 12:00"
python -m reservas reservar MIC-01 Ana "2026-10-28 10:00" "2026-10-28 11:00"
python -m reservas cancelar 1
python -m reservas listar
python -m reservas reiniciar-datos --confirmar
```

Opción `--db RUTA` para usar otro archivo de base de datos.

### Ejemplo de entrada y salida

```
> python -m reservas reservar MIC-01 Ana "2026-10-28 10:00" "2026-10-28 11:00"
Reserva creada: 1
1 | MIC-01 | Ana | 2026-10-28 10:00 | 2026-10-28 11:00 | activa

> python -m reservas reservar MIC-01 Luis "2026-10-28 10:30" "2026-10-28 11:30"
Error: La unidad 'MIC-01' ya tiene una reserva activa que se superpone con el intervalo solicitado.

> python -m reservas disponibilidad MIC-01 "2026-10-28 11:00" "2026-10-28 12:00"
Disponible.

> python -m reservas cancelar 1
Reserva cancelada: 1
1 | MIC-01 | Ana | 2026-10-28 10:00 | 2026-10-28 11:00 | cancelada
```

### Datos y reinicio

- **Inventario inicial:** se carga desde `data/inventario.json`; no se guarda en la base.
- **Dónde persisten las reservas:** en `data/reservas.db` (SQLite). El archivo se crea solo la
  primera vez y está excluido de Git.
- **Reinicio de datos:** `python -m reservas reiniciar-datos --confirmar` **borra todas las reservas, activas y canceladas**. Sin `--confirmar` no borra nada. No reinicia el contador de identificadores.

### Pruebas

```powershell pytest
```

Última ejecución: **47 passed** (Python 3.13.2, pytest 9.2.0). Cubren creación válida,
rechazo de superposición, límites consecutivos, unidades distintas simultáneas, entradas
inválidas, cancelación que conserva el registro y libera el horario, consulta de
disponibilidad y consola. Las pruebas usan bases temporales y nunca tocan `data/reservas.db`.

**Persistencia tras reiniciar:** hay una prueba automática (reabre el repositorio sobre el mismo
archivo y recupera reservas activas y canceladas) y un procedimiento manual con resultados
esperados y observados en [docs/bitacora.md](docs/bitacora.md) (episodio 3, parte B).

### Pendientes y limitaciones

- `BEGIN IMMEDIATE` evita una carrera entre el chequeo y el guardado, pero ninguna prueba lo
  comprueba con dos conexiones simultáneas (la concurrencia está fuera de alcance).
- La consulta de disponibilidad reutiliza `validar_reserva` con un solicitante fijo (`"consulta"`); es un atajo de diseño aceptado.
- Los mensajes de error de argparse están traducidos solo en parte y `--help` sigue en inglés.
- `disponibilidad` devuelve código de salida 1 cuando la unidad está ocupada.
- Se permiten fechas pasadas y no hay límites de duración ni de anticipación.
- La verificación de hora sin cero inicial (`9:00`) se hizo de forma manual; no tiene prueba
  automática.

## 3. Preparación del agente

- **Entorno:** Visual Studio Code [completar versión: Help > About] con GitHub Copilot en modo Agent, plan gratuito. **Modelo:**  copilot selector del chat.
  **Motivo de la elección:** funciona dentro de VS Code, que ya usaba, tiene modo agente que edita archivos y ejecuta comandos con aprobación, y es utilizable con una cuenta gratuita, con varios tokes gratuitos gran ventaja.
  Claude Code y Gemini CLI no tenían un acceso gratuito individual al momento de elegir.
- **Instrucciones:** [.github/copilot-instructions.md](.github/copilot-instructions.md), con reglas de proyecto, formato de fechas, forma de trabajo y permisos. Se amplió antes de cada tarea (persistencia; cancelación, disponibilidad y consola). Es el archivo real, sin
  secretos.
- **Contexto suministrado:** `docs/especificacion.md` y el archivo de instrucciones. Se  excluyeron datos reales, credenciales y otros proyectos: el agente trabajó con solo la carpeta del repositorio abierta.
- **Permisos y controles:** aprobación manual de cada comando de terminal; revisión de cada cambio con `git status`, `git diff` y `pytest` ejecutados por mí; los commits y el push los hice yo (el agente tenía prohibido ejecutarlos). Se probó el comportamiento del agente antes de empezar (ver [docs/bitacora.md](docs/bitacora.md)).
- **Adaptación específica:** regla de turnos consecutivos con intervalos semiabiertos(`inicio_nuevo < fin_existente` y `fin_nuevo > inicio_existente`), con la exigencia de incluir siempre ese caso límite en las pruebas. Evidencia: sección "Regla sobre turnos consecutivos" del archivo de instrucciones, las pruebas de límites consecutivos y la
  mutación del episodio 3A. El chat mostró `copilot-instructions.md` entre las referencias usadas.
- **Retención del progreso:** [docs/bitacora.md](docs/bitacora.md) y el historial de Git, con commits separados para el trabajo del agente y para mis correcciones.


## 4. Registro de decisiones y delegación

### Decisiones significativas

| Decisión | Motivo | Alternativa | Consecuencia |
|---|---|---|---|
| Python y SQLite | Simple, sin dependencias, reproducible | Archivo JSON | Persistencia robusta; requiere SQL |
| Fechas pasadas permitidas | Pruebas deterministas | Rechazarlas | Limitación documentada |
| Transacción `BEGIN IMMEDIATE` | Chequeo y guardado atómicos | Transacción implícita | Sin prueba concurrente |
| Un solo origen de reglas | Consulta y reserva no discrepan | Duplicar validaciones | Atajo del solicitante `"consulta"` |
| Instalación editable en lugar de parches | Forma estándar de ejecutar `python -m reservas` | Mantener `sitecustomize.py` | Hay que activar el entorno |

### Tres episodios de delegación

El detalle de cada episodio (objetivo, contexto e instrucción, resultado del agente, decisión humana y evidencia) está en [docs/bitacora.md](docs/bitacora.md).

| Episodio | Objetivo | Decisión humana | Commits |
|---|---|---|---|
| 1. Modelo y validaciones | R3 a R9 | [completar: aceptar / corregir] | `7ce003b` |
| 2. Persistencia con SQLite | R12 | Corregir (transacción, `close()`, cobertura de canceladas) | agente `dfecc17`, corrección `bf179ee` |
| 3. Cancelación, disponibilidad y consola | R10, R11, CA5 a CA7 | Corregir; rechazar `sitecustomize.py` y la carpeta `reservas/` | 3A `294ec4b` y `cb95707`; 3B `e8d2c54` y `f87bb07` |
