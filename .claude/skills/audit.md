# Skill: audit
# Invocación: /audit
#
# Auditoría multi-rol en una sola pasada. Sin agentes — corre en la conversación actual.
# Lee solo los archivos necesarios. Reporta solo hallazgos reales.

Ejecuta esta auditoría ahora. Lee el código real antes de reportar — no supongas nada.

## Qué leer (mínimo necesario)

- `docs/appendices/status-flow.md` — transiciones de estado oficiales
- `backend/apps/*/views.py` — permisos y uso de responses
- `backend/apps/*/services.py` — lógica de negocio
- `backend/apps/*/selectors.py` — queries N+1
- `backend/config/settings.py` — configuración de producción
- `frontend/src/modules/*/views/*.vue` — estados UI y enums expuestos
- `frontend/src/types/index.ts` — tipos TypeScript

## 4 áreas a revisar

### Área 1 — Producto & Negocio
- ¿Flujos documentados en `docs/` sin implementar?
- ¿Transiciones de estado del flujo oficial sin cobertura?
- ¿TODOs que representen funcionalidad prometida?

### Área 2 — Experiencia de usuario
- ¿Vistas sin estado loading / error / vacío?
- ¿Enums del backend visibles en UI sin traducir?
- ¿Formularios sin validación cliente antes del POST?
- ¿Acciones destructivas sin confirmación?

### Área 3 — Ingeniería
- ¿Lógica de negocio en `views.py` en lugar de `services.py`?
- ¿`except Exception` genéricos?
- ¿Queries N+1 sin `select_related`?
- ¿Operaciones financieras con `float` en lugar de `Decimal`?
- ¿Tipos `any` en TypeScript donde debería haber un tipo concreto?

### Área 4 — Calidad & Seguridad
- ¿Endpoints donde no se verifica `order.customer_id == request.user.id` (IDOR)?
- ¿Endpoints de admin sin `IsAdmin` en `permission_classes`?
- ¿Flujos críticos sin tests (confirmar pago, cancelar pedido)?
- ¿Valores hardcodeados que deberían ser variables de entorno?

## Formato de salida

Reporta solo hallazgos reales. Si un área no tiene hallazgos, omítela.

```
## Auditoría — [fecha]

### Área 1 · Producto & Negocio
🔴/🟠/🟡 — hallazgo — `archivo:línea` — acción

### Área 2 · Experiencia de usuario
...

### Área 3 · Ingeniería
...

### Área 4 · Calidad & Seguridad
...

---
| Prioridad | Área | Hallazgo | Acción |
|---|---|---|---|
| 🔴 | ... | ... | ... |

🔴 Bloqueantes: X · 🟠 Importantes: Y · 🟡 Mejoras: Z
¿Listo para producción?: Sí / No

¿Cuáles corrijo ahora?
```
