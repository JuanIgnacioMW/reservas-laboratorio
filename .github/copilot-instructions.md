# Instrucciones para el agente

## Proyecto
Sistema de reservas de equipos de laboratorio, en consola, con Python.
La especificación está en docs/especificacion.md y es la fuente de verdad.
Si algo no está especificado, no lo inventes: proponé una opción y esperá mi respuesta.

## Stack y estructura
- Python 3.10 o superior. Almacenamiento: SQLite con el módulo `sqlite3` de la biblioteca estándar.
- Única dependencia externa permitida: `pytest`. No agregues otras sin pedirme permiso.
- Código en `src/reservas/`, pruebas en `tests/`, inventario inicial en `data/inventario.json`.
- Los nombres de funciones, variables y mensajes de error van en español.

## Regla sobre turnos consecutivos (adaptación específica)
Un intervalo es semiabierto: incluye el inicio y excluye el fin.
Dos reservas activas de la misma unidad se superponen solo si:
`inicio_nuevo < fin_existente` y `fin_nuevo > inicio_existente`.
Por lo tanto 10:00-11:00 y 11:00-12:00 NO se superponen y ambas son válidas.
Toda prueba de superposición debe incluir este caso límite.
Las reservas canceladas nunca bloquean disponibilidad.

## Formato de fechas
`AAAA-MM-DD HH:MM`, hora local, sin zonas horarias. No uses la fecha actual del sistema
para validar: las fechas pasadas se permiten (ver especificación).

## Forma de trabajar
- Hacé solo lo que te pido en cada tarea; no adelantes funcionalidades de otras tareas.
- Cambios chicos y fáciles de revisar. Explicá qué archivos tocaste.
- Escribí las pruebas junto con el código y ejecutalas con `pytest`.
- Informá el resultado real de los comandos. Si una prueba o un comando falla, mostrá el error completo y no lo presentes como un éxito.
- No afirmes que una prueba pasa si no la ejecutaste.
- No des por hecho que una prueba pasa si no la ejecutaste.

## Permisos y límites
- Trabajá solo dentro de esta carpeta del repositorio.
- No ejecutes `git commit`, `git push`, ni comandos que borren archivos o carpetas.
  Los commits los hago yo después de revisar.
- No instales paquetes sin pedirme permiso.
- No leas ni escribas archivos fuera del repo, ni uses credenciales o datos reales.
- Los solicitantes de las reservas son ficticios.