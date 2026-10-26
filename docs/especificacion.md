# Especificación: sistema de reservas de laboratorio

## 1. Problema
La coordinación de un laboratorio registra pedidos en mensajes y una planilla.
A veces se confirma la misma unidad en horarios superpuestos y otras veces una
cancelación sigue bloqueando el horario. Se necesita consultar disponibilidad,
reservar y cancelar sin perder el historial.

## 2. Alcance
Incluye: leer el inventario precargado, consultar disponibilidad por unidad e
intervalo, crear reservas, cancelarlas y persistir los datos entre reinicios.
Interfaz: consola (CLI).

No incluye: administrar el inventario, autenticación, roles, notificaciones,
pagos, integraciones externas, interfaz gráfica ni concurrencia distribuida.

## 3. Inventario inicial
Cada ID es una unidad física distinta.

| ID      | Equipo                 |
|---------|------------------------|
| MIC-01  | Microscopio digital    |
| MIC-02  | Microscopio digital    |
| OSC-01  | Osciloscopio           |
| MUL-01  | Multímetro             |
| FUE-01  | Fuente de alimentación |

## 4. Reglas
- R1. Una reserva tiene: identificador, unidad, solicitante, inicio, fin y estado
  (activa o cancelada). Una unidad por reserva.
- R2. Una reserva activa ocupa el intervalo; una cancelada no bloquea.
- R3. La unidad debe existir en el inventario.
- R4. El solicitante no puede estar vacío ni tener solo espacios.
- R5. Fechas y horas deben ser válidas y estar en el formato definido.
- R6. El inicio debe ser estrictamente anterior al fin.
- R7. Se rechaza la reserva si se superpone con otra activa de la misma unidad.
- R8. Se permiten límites consecutivos: 10:00-11:00 y 11:00-12:00 no se superponen.
- R9. Unidades distintas pueden reservarse en el mismo horario.
- R10. La consulta de disponibilidad aplica exactamente las mismas reglas que la
  creación (validaciones y superposición).
- R11. Cancelar conserva identificador y datos, cambia el estado a "cancelada"
  y libera el intervalo. No se borra nada.
- R12. Las reservas y sus estados se guardan y se recuperan al reiniciar.

## 5. Supuestos (decisiones propias)
- Zona horaria: hora local del laboratorio, sin conversión de zonas.
- Formato de fecha y hora: `AAAA-MM-DD HH:MM` (24 h), sin segundos.
- Fechas pasadas: se permiten, para que las pruebas sean deterministas y no
  dependan del reloj. Queda como limitación documentada.
- Sin límite de duración ni de anticipación.
- Cancelar una reserva ya cancelada o inexistente devuelve un error claro.
- Los solicitantes son ficticios.
- Almacenamiento: SQLite (biblioteca estándar de Python), archivo local.

## 6. Criterios de aceptación
- CA1. Con MIC-01 reservado 10:00-11:00 el mismo día, reservar MIC-01
  10:30-11:30 es rechazado.
- CA2. Con esa misma reserva, MIC-01 11:00-12:00 es aceptado.
- CA3. Con esa misma reserva, MIC-02 10:00-11:00 es aceptado.
- CA4. Se rechaza: unidad desconocida, solicitante vacío o de solo espacios,
  fecha inválida y inicio igual o posterior al fin.
- CA5. Tras cancelar, la reserva sigue listada como cancelada con los mismos
  datos, y el intervalo vuelve a estar disponible.
- CA6. Tras reiniciar la aplicación sin borrar datos, las reservas activas y
  canceladas siguen presentes.
- CA7. La consulta de disponibilidad da el mismo resultado que el intento de
  reserva para cada caso anterior.
