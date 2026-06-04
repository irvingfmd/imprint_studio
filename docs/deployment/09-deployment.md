# Deployment

## Imprint Studio

Versión: 2.0

Estado: Aprobado para implementación

---

# Propósito

Este documento define la estrategia oficial de despliegue para Imprint Studio.

Describe:

* Entornos
* Infraestructura
* Configuración
* Seguridad
* Backups
* Monitoreo
* Escalabilidad

Este documento es la fuente oficial para:

* DevOps
* Backend
* Infraestructura
* CI/CD
* Producción

---

# Filosofía

## MVP Primero

El objetivo inicial es:

```text
Lanzar rápido.
Mantener costos bajos.
Reducir complejidad.
```

---

## Regla

No implementar infraestructura empresarial innecesaria durante el MVP.

---

# Entornos

## Local

Uso:

```text
Desarrollo diario.
```

---

## Staging

Uso:

```text
Pruebas antes de producción.
```

---

## Production

Uso:

```text
Clientes reales.
```

---

# Arquitectura General

```text
Frontend (Vue 3)
        │
        ▼
   Cloudflare
        │
        ▼
Backend (Django)
        │
        ▼
 PostgreSQL
        │
        ▼
 Cloudinary
```

---

# Stack Oficial

| Componente    | Tecnología            |
| ------------- | --------------------- |
| Frontend      | Vue 3                 |
| Backend       | Django 5              |
| API           | Django REST Framework |
| Base de Datos | PostgreSQL            |
| Archivos      | Cloudinary            |
| Email         | Brevo                 |
| Autenticación | JWT                   |
| OTP           | WhatsApp Business     |
| Web Server    | Nginx                 |
| App Server    | Gunicorn              |
| SSL           | Let's Encrypt         |
| DNS           | Cloudflare            |

---

# Estructura del Proyecto

```text
imprint-studio/
│
├── backend/
│
├── frontend/
│
├── docs/
│
├── .env
│
├── .env.example
│
├── .gitignore
│
└── README.md
```

---

# Variables de Entorno

## Regla

Nunca guardar secretos en el repositorio.

---

## Archivo

```text
.env
```

---

# Backend

## Django Secret Key

```env
DJANGO_SECRET_KEY=
```

---

## Debug

```env
DEBUG=False
```

---

## Allowed Hosts

```env
ALLOWED_HOSTS=
```

---

## Database

```env
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

---

## JWT

```env
JWT_ACCESS_MINUTES=60
JWT_REFRESH_DAYS=7
```

---

## Cloudinary

```env
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

---

## Brevo

```env
BREVO_API_KEY=
```

---

## WhatsApp

```env
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_ID=
```

---

# Configuración Local

## Base de Datos

```text
SQLite
```

permitida únicamente para desarrollo.

---

## Producción

Obligatorio:

```text
PostgreSQL
```

---

# PostgreSQL

## Recomendación Inicial

Plan básico.

---

## Configuración

Timezone:

```text
America/Mexico_City
```

---

## Encoding

```text
UTF-8
```

---

# Cloudinary

## Archivos Permitidos

```text
JPG
JPEG
PNG
PDF
STL
OBJ
3MF
```

---

# Regla

Nunca almacenar archivos dentro del servidor.

---

# Backend Deployment

## Aplicación

```text
Django 5
```

---

## WSGI

```text
Gunicorn
```

---

## Comando

```bash
gunicorn config.wsgi:application
```

---

# Nginx

## Funciones

* Reverse Proxy
* SSL
* Seguridad
* Compresión

---

## Flujo

```text
Internet
    ↓
Cloudflare
    ↓
Nginx
    ↓
Gunicorn
    ↓
Django
```

---

# SSL

## Proveedor

```text
Let's Encrypt
```

---

## Renovación

Automática.

---

# Frontend Deployment

## Build

```bash
npm run build
```

---

## Resultado

```text
dist/
```

---

# Hosting Recomendado

## Opción MVP

```text
Vercel
```

---

## Opción Alternativa

```text
Netlify
```

---

## Opción VPS

```text
Nginx
```

---

# Backend Hosting

## Opción MVP

```text
Hetzner VPS
```

---

## Alternativas

```text
DigitalOcean

Vultr

Contabo
```

---

# Recomendación

Evitar AWS durante el MVP.

---

## Razones

* Complejidad.
* Costos.
* Curva de aprendizaje.

---

# VPS Inicial

## CPU

```text
2 vCPU
```

---

## RAM

```text
4 GB
```

---

## Disco

```text
40 GB SSD
```

---

## Suficiente para

```text
Primeros cientos de clientes.
```

---

# Backups

## Base de Datos

Frecuencia:

```text
Diaria
```

---

## Retención

```text
30 días
```

---

# Archivos

Cloudinary mantiene redundancia.

---

# Regla

Nunca depender de un único backup.

---

# Logs

## Django

Guardar:

```text
Errors

Warnings

Critical
```

---

## Nginx

Guardar:

```text
Access Logs

Error Logs
```

---

# Rotación

Automática.

---

# Monitoreo

## MVP

Herramientas simples.

---

## Uptime

Recomendado:

```text
UptimeRobot
```

---

## Métricas

Monitorear:

```text
CPU

RAM

Disk

Database
```

---

# Seguridad

## DEBUG

Siempre:

```env
DEBUG=False
```

en producción.

---

# CSRF

Habilitado.

---

# CORS

Restringido.

---

## Producción

Permitir únicamente:

```text
Frontend oficial.
```

---

# Passwords

Nunca almacenar texto plano.

---

## Django

Utilizar:

```text
PBKDF2
```

por defecto.

---

# JWT

Expiración obligatoria.

---

# Rate Limiting

Aplicar a:

```text
OTP

Login

Register
```

---

# Git

## Rama Principal

```text
main
```

---

## Desarrollo

```text
develop
```

---

# Flujo

```text
feature/*
    ↓
develop
    ↓
main
```

---

# CI/CD

## MVP

Opcional.

---

## Recomendado

GitHub Actions.

---

# Pipeline Mínimo

```text
Install

Lint

Tests

Build
```

---

# Validaciones Antes de Deploy

## Backend

```bash
python manage.py check
```

---

## Migraciones

```bash
python manage.py makemigrations

python manage.py migrate
```

---

## Tests

```bash
pytest
```

---

## Frontend

```bash
npm run build
```

---

# Checklist Pre-Producción

* DEBUG=False
* HTTPS activo
* PostgreSQL configurado
* Backups configurados
* Cloudinary configurado
* JWT configurado
* CORS configurado
* Rate Limiting configurado
* Variables de entorno configuradas
* Logs configurados

---

# Checklist Post-Producción

* Registro funciona
* OTP funciona
* Login funciona
* Crear pedidos funciona
* Subir archivos funciona
* Crear cotizaciones funciona
* Confirmar pagos funciona
* Dashboard funciona

---

# Escalabilidad

## Etapa 1

```text
0 - 500 pedidos/mes
```

Infraestructura actual.

---

## Etapa 2

```text
500 - 2000 pedidos/mes
```

Agregar:

```text
Redis
Celery
```

---

## Etapa 3

```text
2000+ pedidos/mes
```

Agregar:

```text
Load Balancer

Multiple Django Instances
```

---

# Futuro

Cuando el negocio crezca:

```text
Redis

Celery

S3

CDN

Monitoring avanzado

IA
```

---

# Restricción MVP

No implementar:

```text
Kubernetes

Microservicios

Event Sourcing

Arquitecturas Distribuidas
```

---

## Razón

Complejidad innecesaria.

---

# Recuperación ante Desastres

## Base de Datos

Restaurar desde backup.

---

## Archivos

Restaurar desde Cloudinary.

---

## Código

Restaurar desde GitHub.

---

# Objetivo

Mantener una infraestructura:

* Simple.
* Económica.
* Escalable.
* Segura.
* Fácil de administrar.

---

# Resultado Esperado

Imprint Studio debe poder operar de forma estable con clientes reales utilizando infraestructura mínima y costos controlados.

---

# Estado del Documento

Versión: 2.0

Estado:

Aprobado para implementación.

Fuente oficial para:

* Infraestructura
* DevOps
* Producción
* CI/CD
* Escalabilidad

Fin del documento.
