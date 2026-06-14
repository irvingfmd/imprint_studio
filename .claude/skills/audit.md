# Skill: audit
# Invocación: /audit [área]
# Área opcional: producto | ux | ingenieria | calidad | todo (default: todo)
#
# Lanza 4 agentes especializados en paralelo y agrega sus hallazgos.
# Cada agente lee el código real — no confía en resúmenes ni en CLAUDE.md.

Ejecuta los siguientes pasos:

## Paso 1 — Lanzar 4 agentes en paralelo

Lanza estos 4 agentes **en el mismo mensaje** (un solo bloque de tool calls):

---

### Agente 1 · Producto & Negocio
**subagent_type:** `Explore`
**prompt:**
```
Eres un equipo de Product Owner + Business Analyst + Project Manager auditando
el proyecto Imprint Studio (Django + Vue 3).

Lee los archivos relevantes del proyecto y responde SOLO con hallazgos reales
que encuentres en el código — no inventes problemas.

Documentación de referencia:
- docs/architecture/01-business-rules.md
- docs/architecture/04-api-specification.md
- docs/appendices/status-flow.md
- CLAUDE.md (sección "Estado actual")

Revisa:
1. ¿Hay flujos de negocio documentados en docs/ que no están implementados?
2. ¿Las transiciones de estado en status-flow.md tienen cobertura completa en backend/apps/production/services.py?
3. ¿Las reglas de pago en docs/business/06-payments-and-refunds.md están implementadas en backend/apps/payments/?
4. ¿Hay TODOs o FIXMEs en el código que representen funcionalidad prometida sin terminar?
5. ¿Hay deuda técnica que bloquee escalar el negocio?

Formato de respuesta (solo hallazgos reales, con archivo y línea):
🔴 Alta | 🟠 Media | 🟡 Baja — descripción — archivo:línea — acción recomendada

Si no encuentras hallazgos en algún punto, escribe "Sin hallazgos."
```

---

### Agente 2 · Experiencia de usuario
**subagent_type:** `Explore`
**prompt:**
```
Eres un equipo de UX/UI Designer + Technical Writer + Support auditando
el frontend de Imprint Studio (Vue 3 + TypeScript + Tailwind CSS).

Lee los archivos de frontend en frontend/src/ y responde SOLO con hallazgos
reales que encuentres en el código.

Revisa:
1. ¿Alguna vista no tiene estado de loading, error o vacío?
2. ¿Hay valores raw del backend (enums en MAYÚSCULAS) mostrándose directamente en la UI?
   Busca en los templates Vue: v-if, {{ }}, donde se usen valores como status, payment_status, priority.
3. ¿Hay mensajes de error que no le dicen al usuario qué hacer a continuación?
4. ¿Hay acciones destructivas (cancelar, rechazar) sin modal de confirmación?
5. ¿Hay formularios sin validación del lado del cliente antes del POST?
6. ¿Los componentes manejan el estado disabled durante loading para evitar doble submit?
7. ¿La documentación en CLAUDE.md refleja el estado real del frontend?

Formato de respuesta (solo hallazgos reales, con archivo y línea):
🔴 Alta | 🟠 Media | 🟡 Baja — descripción — archivo:línea — acción recomendada

Si no encuentras hallazgos en algún punto, escribe "Sin hallazgos."
```

---

### Agente 3 · Ingeniería de software
**subagent_type:** `Explore`
**prompt:**
```
Eres un equipo de Software Architect + Backend Developer + Frontend Developer + DBA
auditando Imprint Studio (Django 5.1 + DRF + Vue 3 + SQLite/PostgreSQL).

Lee el código real en backend/apps/ y frontend/src/ y responde SOLO con hallazgos
reales que encuentres.

Revisa:

ARQUITECTURA:
1. ¿Hay lógica de negocio en views.py en lugar de services.py?
2. ¿Todos los endpoints usan success_response/error_response/created_response de core/responses.py?
3. ¿Hay acoplamiento directo entre apps (imports cruzados fuera de los patrones establecidos)?

BACKEND:
4. ¿Hay except Exception genéricos que ocultan errores reales?
5. ¿Las operaciones que modifican múltiples modelos usan transaction.atomic?
6. ¿Los serializers validan todos los campos de entrada con tipos correctos?

FRONTEND:
7. ¿Hay tipos TypeScript con `any` donde debería haber un tipo concreto?
8. ¿Los servicios en frontend/src/modules/*/services/ manejan errores de red?

BASE DE DATOS:
9. ¿Hay queries en selectors.py que generan N+1 sin select_related/prefetch_related?
10. ¿Los campos usados en filter() frecuentes tienen db_index=True en el modelo?
11. ¿Hay operaciones financieras usando float en lugar de Decimal?

Formato de respuesta (solo hallazgos reales, con archivo y línea):
🔴 Alta | 🟠 Media | 🟡 Baja — descripción — archivo:línea — acción recomendada

Si no encuentras hallazgos en algún punto, escribe "Sin hallazgos."
```

---

### Agente 4 · Calidad & Seguridad
**subagent_type:** `Explore`
**prompt:**
```
Eres un equipo de QA Engineer + Security/AppSec + DevOps auditando
Imprint Studio (Django 5.1 + DRF).

Lee el código real en backend/ y responde SOLO con hallazgos reales.

SEGURIDAD (OWASP Top 10 + patrones del proyecto):
1. ¿Algún endpoint de cliente permite acceder a recursos de otro usuario (IDOR)?
   Revisa que cada view verifique order.customer_id == request.user.id antes de responder.
2. ¿Algún endpoint de admin no tiene IsAdmin en permission_classes?
3. ¿Hay datos sensibles (tokens, OTPs, teléfonos) en logs con nivel INFO o superior?
4. ¿Hay endpoints sin autenticación que deberían tenerla?
5. ¿El settings.py tiene configuración segura para producción (DEBUG, SECRET_KEY, ALLOWED_HOSTS)?

CALIDAD / TESTS:
6. ¿Hay flujos críticos sin tests? (confirmar pago, cambiar estado, cancelar pedido)
7. ¿Los tests de vistas verifican permisos cruzados (cliente A no puede ver pedido de cliente B)?
8. ¿Los tests de servicios cubren los casos de error además del happy path?

DEVOPS:
9. ¿Hay valores hardcodeados que deberían estar en variables de entorno?
10. ¿Las dependencias en requirements.txt tienen versiones fijas (sin >=)?
11. ¿Hay archivos sensibles que podrían estar fuera del .gitignore?

Formato de respuesta (solo hallazgos reales, con archivo y línea):
🔴 Alta | 🟠 Media | 🟡 Baja — descripción — archivo:línea — acción recomendada

Si no encuentras hallazgos en algún punto, escribe "Sin hallazgos."
```

---

## Paso 2 — Agregar resultados

Cuando los 4 agentes terminen, consolida sus hallazgos en este formato:

```
## Auditoría Imprint Studio — [fecha]

### Hallazgos por área

#### Producto & Negocio
[resultados del Agente 1]

#### Experiencia de usuario
[resultados del Agente 2]

#### Ingeniería de software
[resultados del Agente 3]

#### Calidad & Seguridad
[resultados del Agente 4]

---

### Tabla de acción consolidada

| Prioridad | Área | Hallazgo | Archivo | Acción |
|---|---|---|---|---|
| 🔴 | ... | ... | ... | ... |
| 🟠 | ... | ... | ... | ... |
| 🟡 | ... | ... | ... | ... |

### Resumen ejecutivo
- 🔴 Bloqueantes: X
- 🟠 Importantes: Y
- 🟡 Mejoras: Z
- ¿Listo para producción?: [Sí / No — razón]

¿Cuáles corrijo ahora?
```
