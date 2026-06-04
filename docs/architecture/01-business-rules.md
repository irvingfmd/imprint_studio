# Business Rules

## Imprint Studio

Versión: 1.0

Estado: Aprobado para implementación

---

# Propósito

Este documento define las reglas de negocio oficiales de Imprint Studio.

Todas las funcionalidades del sistema, API, base de datos, automatizaciones y futuras integraciones deben respetar las reglas establecidas en este documento.

En caso de conflicto entre documentos, las reglas definidas aquí tienen prioridad sobre la implementación técnica.

---

# Objetivo del Negocio

Imprint Studio ofrece servicios de impresión 3D personalizada bajo demanda.

Los clientes pueden solicitar piezas mediante referencias visuales o archivos 3D listos para impresión.

El negocio opera bajo un esquema de cotización previa, pago de anticipo, producción, liquidación y entrega.

---

# Principios Operativos

## Automation First

La automatización debe utilizar reglas determinísticas.

Las decisiones operativas no dependen de inteligencia artificial.

---

## Human Approval Required

Las decisiones críticas requieren intervención humana.

Incluye:

* Aprobación de cotizaciones.
* Confirmación de pagos.
* Reembolsos.
* Cancelaciones.
* Cambios de configuración.
* Entregas.

---

## AI Later

La inteligencia artificial es una capacidad futura.

El sistema debe operar correctamente sin depender de:

* ChatGPT
* Claude
* Gemini
* Copilot
* Cualquier servicio externo de IA

---

# Tipos de Solicitudes

---

# Type A - Reference Request

Solicitud basada en referencias visuales.

El cliente puede subir:

* Fotografías
* Capturas de pantalla
* Imágenes de internet
* Bocetos
* Diseños conceptuales

---

## Información Requerida

* Descripción
* Tamaño aproximado
* Color deseado
* Cantidad

---

## Estado Inicial

```text
RECEIVED
```

---

## Restricciones

No puede generarse una cotización hasta que exista un modelo imprimible.

Puede requerir:

* Modelado 3D
* Adaptación de modelo existente
* Búsqueda de modelo compatible

---

# Type B - Printable File Request

Solicitud basada en archivos listos para impresión.

---

## Formatos Permitidos

```text
STL
3MF
OBJ
```

---

## Validaciones Iniciales

* Integridad del archivo
* Formato soportado
* Tamaño válido
* Archivo legible

---

## Estado Inicial

```text
PENDING_ANALYSIS
```

---

# Prioridades

Cada solicitud debe tener una prioridad.

---

# NORMAL

Multiplicador:

```text
1.00
```

Tiempo estimado:

```text
5 a 7 días hábiles
```

---

# URGENT

Multiplicador:

```text
1.30
```

Incremento:

```text
30%
```

Tiempo estimado:

```text
2 a 3 días hábiles
```

---

# EXPRESS

Multiplicador:

```text
1.50
```

Incremento:

```text
50%
```

Tiempo estimado:

```text
24 a 48 horas hábiles
```

---

# Días Hábiles

Se consideran días hábiles:

```text
Lunes a Viernes
```

---

No se consideran:

* Sábados
* Domingos
* Días festivos configurados

---

# Flujo Principal del Negocio

```text
Cliente
↓
Registro
↓
OTP
↓
Login
↓
Solicitud
↓
Revisión Técnica
↓
Cotización
↓
Aceptación
↓
Pago
↓
Producción
↓
Entrega
↓
Finalización
```

---

# Estados Oficiales

---

# RECEIVED

Solicitud por referencia recibida.

---

# PENDING_ANALYSIS

Archivo recibido y pendiente de revisión.

---

# QUOTED

Cotización generada.

Esperando respuesta del cliente.

---

# APPROVED

Cotización aceptada.

---

# PENDING_DEPOSIT

Esperando anticipo.

---

# DEPOSIT_PAID

Anticipo confirmado.

Producción autorizada.

---

# PRINTING

Pieza en impresión.

---

# POST_PROCESSING

Pieza en postprocesado.

---

# READY

Producción terminada.

Lista para entrega.

---

# PENDING_BALANCE

Saldo pendiente.

---

# FULLY_PAID

Pago liquidado.

---

# DELIVERED

Pedido entregado.

---

# CANCELLED

Pedido cancelado.

---

# Flujo de Estados Permitido

## Solicitud por Referencia

```text
RECEIVED
↓
QUOTED
↓
APPROVED
↓
PENDING_DEPOSIT
↓
DEPOSIT_PAID
↓
PRINTING
↓
POST_PROCESSING
↓
READY
↓
PENDING_BALANCE
↓
FULLY_PAID
↓
DELIVERED
```

---

## Solicitud con Archivo

```text
PENDING_ANALYSIS
↓
QUOTED
↓
APPROVED
↓
PENDING_DEPOSIT
↓
DEPOSIT_PAID
↓
PRINTING
↓
POST_PROCESSING
↓
READY
↓
PENDING_BALANCE
↓
FULLY_PAID
↓
DELIVERED
```

---

# Flujo con Pago Total

```text
APPROVED
↓
FULLY_PAID
↓
PRINTING
↓
POST_PROCESSING
↓
READY
↓
DELIVERED
```

---

# Pagos

---

# Modalidades Permitidas

## Opción 1

```text
50% Anticipo
50% Contra Entrega
```

---

## Opción 2

```text
100% Anticipado
```

---

# Beneficio por Pago Total

Descuento:

```text
5%
```

Aplicado sobre el precio final.

---

# Métodos de Pago Permitidos

## Transferencia Bancaria

Configurada desde administración.

---

## Efectivo

Disponible únicamente para:

* Recogida en taller.
* Entrega local autorizada.

---

# Anticipos

El anticipo es obligatorio para iniciar producción.

---

## Tiempo Límite

```text
72 horas
```

---

## Si el Cliente No Paga

El sistema debe cancelar automáticamente la solicitud.

Estado final:

```text
CANCELLED
```

---

# Producción

La producción únicamente puede iniciar cuando exista:

```text
DEPOSIT_PAID
```

o

```text
FULLY_PAID
```

---

No se permite imprimir pedidos sin pago confirmado.

---

# Datos Oficiales de Producción

Todos los cálculos deben basarse en información proveniente de:

```text
Bambu Studio
```

---

Datos requeridos:

* Peso real en gramos.
* Tiempo real de impresión.

---

No se permiten estimaciones manuales como fuente principal de cálculo.

---

# Entregas

---

# Modalidades Disponibles

## Recogida en Taller

El cliente recoge personalmente.

---

## Envío a Domicilio

El cliente proporciona dirección completa.

---

# Información Obligatoria para Envíos

* Calle
* Número
* Colonia
* Código Postal
* Ciudad
* Estado
* País
* Referencias

---

# Dirección de Envío

Las direcciones deben almacenarse en:

```text
shipping_addresses
```

---

No deben almacenarse directamente dentro de:

```text
orders
```

---

# Justificación

Permite:

* Historial de direcciones
* Escalabilidad
* Mejor normalización
* Menos campos nulos

---

# Costos de Envío

El costo de envío se captura manualmente.

---

## Motivo

Factores variables:

* Distancia
* Clima
* Urgencia
* Tipo de paquete
* Transportista

---

# Reembolsos

---

# Antes del Laminado

Reembolso:

```text
100%
```

---

# Después del Laminado

Reembolso:

```text
70%
```

---

# Durante la Impresión

Reembolso:

```text
0%
```

---

# Después de la Impresión

Reembolso:

```text
0%
```

---

# Cancelación por Falta de Anticipo

Reembolso:

```text
100%
```

---

# Política de Reembolsos

El sistema únicamente calcula el porcentaje sugerido.

La aprobación final siempre corresponde al administrador.

---

# Confirmación de Pagos

La confirmación de pagos es manual.

---

# Evidencias Permitidas

* Imagen
* PDF
* Confirmación administrativa

---

# Confirmación Manual

Debe existir soporte para:

```text
manual_confirmation = true
```

---

# Horarios de Atención

Los horarios deben configurarse desde administración.

---

# Configuración Editable

* Días laborables
* Horarios
* Notas
* Restricciones

---

# Días Festivos

Los días festivos deben configurarse desde administración.

---

Los tiempos de entrega deben excluir:

* Sábados
* Domingos
* Festivos

---

# Moneda Oficial

```text
MXN
```

---

# Zona Horaria Oficial

```text
America/Mexico_City
```

---

# Formato Telefónico

Todos los números deben almacenarse utilizando:

```text
E.164
```

Ejemplo:

```text
+5219611234567
```

---

# Restricciones del MVP

Durante el MVP no se permite:

* Cotización automática mediante IA.
* Aprobación automática de pagos.
* Reembolsos automáticos.
* Decisiones financieras automatizadas.
* Cambios de configuración por IA.

---

# Regla Fundamental

La automatización puede ejecutar procesos operativos.

La inteligencia artificial puede sugerir acciones.

Las decisiones financieras, comerciales y operativas siempre permanecen bajo control humano.
