AutoSchedule
===========

Backend para un sistema de auto‑programación que distribuye tareas según disponibilidad,
prioridad y fechas límite.

Roles resumidos
---------------

- **Hugo**: Arquitectura, seguridad y despliegue — configura el repositorio, JWT,
	manejo global de errores, health check, CI/CD y despliegue con Postgres en la nube.
- **Luque**: Motor de auto‑programación — diseña `Task`/`Session` y el algoritmo que
	genera el calendario (con transacciones y pruebas de integración).
- **Andrei**: Disponibilidades y filtros — modelos/endpoints de `Availability`,
	validaciones y filtros avanzados con `django-filter`, además de pruebas.
- **Anderson**: API y documentación — CRUD de `Task`, perfiles, reprogramación
	y documentación Swagger/OpenAPI.