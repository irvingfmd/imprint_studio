# AI Roadmap

## Imprint Studio

Versión: 2.0

Estado: Planeación Estratégica

---

# Propósito

Este documento define la estrategia oficial para incorporar Inteligencia Artificial en Imprint Studio.

La IA no forma parte del MVP.

La IA será implementada únicamente cuando existan:

* Clientes reales.
* Solicitudes reales.
* Historial suficiente.
* Beneficio económico comprobable.

---

# Filosofía

## Principio Principal

```text
Automatización primero.
IA después.
```

---

# Regla Fundamental

Ninguna funcionalidad crítica del negocio debe depender de IA durante el MVP.

---

# Razón

Los modelos de IA:

* Generan costos.
* Generan complejidad.
* Generan dependencia externa.
* Pueden equivocarse.

---

# Objetivo del MVP

Operar completamente sin:

```text
ChatGPT

Claude

Gemini

OpenAI

Anthropic

Google AI
```

---

# Situación Actual

El MVP debe funcionar utilizando únicamente:

* Django
* Vue
* PostgreSQL
* Cloudinary
* WhatsApp
* Bambu Studio

---

# Preparación Actual

Aunque la IA no se utilizará inicialmente, la arquitectura ya está preparada.

---

# Campos Reservados

Tabla:

```text
orders
```

---

## Campos

```text
ai_analysis

ai_notes

ai_confidence

ai_category
```

---

# Restricción MVP

Durante el MVP:

```text
Todos los campos AI deben permanecer vacíos.
```

---

# Objetivo del Roadmap

Incorporar IA gradualmente.

Cada etapa debe:

* Ahorrar tiempo.
* Reducir trabajo manual.
* Mantener control humano.
* Tener retorno de inversión.

---

# Fase 0

# MVP Sin IA

Estado:

```text
OBLIGATORIO
```

---

## Funcionalidades

* Registro.
* OTP.
* Solicitudes.
* Cotizaciones.
* Pagos.
* Producción.
* Envíos.
* Dashboard.

---

## IA

```text
NO
```

---

## Responsable

Administrador.

---

# Criterio para Avanzar

Mínimo:

```text
100 solicitudes reales
```

o

```text
3 meses de operación
```

---

# Fase 1

# Agente de Clasificación

Estado:

```text
PRIMERA IMPLEMENTACIÓN IA
```

---

# Problema

Actualmente:

```text
Cliente envía imagen
↓
Administrador revisa
↓
Administrador determina complejidad
```

---

# Objetivo

Reducir tiempo de revisión inicial.

---

# Entrada

```text
Imagen

Descripción
```

---

# Salida

```text
Categoría sugerida

Complejidad estimada

Notas sugeridas

Nivel de confianza
```

---

# Ejemplo

Entrada:

```text
Figura anime de 20 cm
```

---

Salida:

```json
{
  "category": "ANIME_FIGURE",
  "complexity": "MEDIUM",
  "confidence": 0.92
}
```

---

# Restricción

La IA no puede:

* Aprobar pedidos.
* Generar precios.
* Modificar estados.

---

# Solo Puede

```text
Sugerir
```

---

# Campos Utilizados

```text
ai_analysis

ai_category

ai_confidence

ai_notes
```

---

# Posibles Tecnologías

## Opción 1

```text
OpenAI Vision
```

---

## Opción 2

```text
Claude Vision
```

---

## Opción 3

```text
Gemini Vision
```

---

# Recomendación

Esperar hasta tener datos reales.

---

# Fase 2

# Agente de Cotización Asistida

Estado:

```text
DESPUÉS DE FASE 1
```

---

# Objetivo

Reducir trabajo administrativo.

---

# Entrada

```text
Resultado de laminado

Configuración del negocio
```

---

# Salida

```text
Cotización sugerida
```

---

# Importante

La IA no calcula.

La IA utiliza:

```text
QuoteCalculatorService
```

---

# La Fórmula Oficial Sigue Siendo

```text
05-cost-calculator.md
```

---

# La IA Solo Puede

```text
Proponer
```

---

# El Administrador Debe

```text
Aprobar
```

---

# Ejemplo

```text
IA:
Precio sugerido: $450 MXN

Administrador:
Aprueba o modifica.
```

---

# Restricción

La IA no puede:

* Aprobar cotizaciones.
* Enviar cotizaciones.
* Cambiar precios finales.

---

# Fase 3

# Agente de Producción

Estado:

```text
MEDIANO PLAZO
```

---

# Problema

Muchas solicitudes simultáneas.

---

# Objetivo

Priorizar automáticamente.

---

# Entrada

```text
Cola de pedidos

Prioridades

Fechas límite

Capacidad disponible
```

---

# Salida

```text
Orden sugerido de producción
```

---

# Ejemplo

```text
1. Pedido #84
2. Pedido #79
3. Pedido #102
```

---

# Beneficio

Optimización operativa.

---

# Restricción

La decisión final sigue siendo humana.

---

# Fase 4

# Agente de Atención al Cliente

Estado:

```text
LARGO PLAZO
```

---

# Objetivo

Responder preguntas frecuentes.

---

# Casos

```text
¿Cuándo estará listo?

¿Cuánto debo?

¿Ya enviaron mi pedido?

¿Qué métodos de pago aceptan?
```

---

# Fuente de Datos

API oficial.

---

# Restricción

No puede:

* Confirmar pagos.
* Aprobar reembolsos.
* Modificar pedidos.

---

# Fase 5

# Agente de Marketing

Estado:

```text
OPCIONAL
```

---

# Objetivo

Generar contenido.

---

# Casos

```text
Instagram

Facebook

TikTok

Promociones
```

---

# Ejemplo

Entrada:

```text
Figura de Goku terminada
```

---

Salida:

```text
Texto para publicación
Hashtags
Descripción
```

---

# Restricción

No publica automáticamente.

---

# Fase 6

# Agente de Analítica

Estado:

```text
AVANZADO
```

---

# Objetivo

Detectar tendencias.

---

# Análisis

```text
Categorías más vendidas

Material más utilizado

Margen promedio

Tasa de cancelación

Tasa de reembolso
```

---

# Resultado

Reportes ejecutivos.

---

# Datos Necesarios

Mínimo:

```text
500 pedidos históricos
```

---

# Fase 7

# IA Predictiva

Estado:

```text
FUTURO
```

---

# Objetivo

Predecir:

* Demanda.
* Carga de trabajo.
* Material requerido.

---

# Ejemplo

```text
La próxima semana se esperan
20 pedidos adicionales.
```

---

# Requisitos

Historial amplio.

---

# IA Local

Actualmente:

```text
NO RECOMENDADA
```

---

# Razones

* Complejidad.
* Hardware.
* Mantenimiento.

---

# Alternativa Recomendada

APIs externas.

---

# Criterios para Incorporar IA

Toda nueva integración debe cumplir:

---

## Regla 1

Reducir trabajo manual.

---

## Regla 2

Generar ahorro económico.

---

## Regla 3

Ser medible.

---

## Regla 4

No afectar operaciones.

---

## Regla 5

Tener supervisión humana.

---

# Funciones Prohibidas para IA

La IA nunca podrá:

---

## Confirmar Pagos

```text
PROHIBIDO
```

---

## Autorizar Reembolsos

```text
PROHIBIDO
```

---

## Cambiar Configuración Financiera

```text
PROHIBIDO
```

---

## Modificar Costos

```text
PROHIBIDO
```

---

## Eliminar Información

```text
PROHIBIDO
```

---

## Aprobar Producción

```text
PROHIBIDO
```

---

# Funciones Permitidas

La IA sí podrá:

---

## Clasificar

```text
PERMITIDO
```

---

## Sugerir

```text
PERMITIDO
```

---

## Analizar

```text
PERMITIDO
```

---

## Resumir

```text
PERMITIDO
```

---

## Priorizar

```text
PERMITIDO
```

---

# Métricas para Evaluar IA

Antes y después de implementar IA medir:

```text
Tiempo de cotización

Tiempo de revisión

Tiempo de respuesta

Errores operativos

Conversión de ventas
```

---

# ROI Esperado

La IA debe demostrar:

```text
Más ahorro que costo.
```

---

# Decisión Estratégica

La IA se incorpora únicamente cuando:

```text
Genere valor real.
```

No por moda.

No por marketing.

No por tendencia.

---

# Visión Final

Imprint Studio debe evolucionar hacia una plataforma donde:

* La automatización maneja procesos.
* La IA asiste decisiones.
* El administrador mantiene control.
* Los clientes reciben respuestas más rápidas.

---

# Objetivo

Construir un negocio rentable primero.

Incorporar IA después.

---

# Estado del Documento

Versión: 2.0

Estado:

Planeación Estratégica.

Fuente oficial para:

* Futuras Integraciones IA
* Arquitectura
* Automatizaciones Inteligentes
* Roadmap Tecnológico

Fin del documento.
