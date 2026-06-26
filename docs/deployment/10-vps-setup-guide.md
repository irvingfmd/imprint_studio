# Guía de configuración del VPS

## Imprint Studio

Versión: 1.0

Estado: Lista para ejecución

---

# Requisitos previos

Antes de empezar necesitas:

* Un VPS con Ubuntu 22.04+ (Hetzner recomendado: 2 vCPU, 4 GB RAM, 40 GB SSD)
* Un dominio apuntando a Cloudflare
* Cuenta de Cloudinary (archivos)
* Cuenta de Brevo (emails)
* Repositorio en GitHub con el código de Imprint Studio

---

# Paso 1 — Acceso inicial y seguridad

## Conectar al VPS

```bash
ssh root@TU_IP_DEL_VPS
```

## Crear usuario de deploy

```bash
adduser deploy
usermod -aG sudo deploy
```

## Configurar SSH keys

Desde tu máquina local:

```bash
ssh-copy-id deploy@TU_IP_DEL_VPS
```

## Deshabilitar acceso root por SSH

```bash
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd
```

## Firewall

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

---

# Paso 2 — Instalar dependencias del sistema

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
  python3.12 python3.12-venv python3.12-dev \
  postgresql postgresql-contrib \
  nginx \
  certbot python3-certbot-nginx \
  git curl
```

Si Python 3.12 no está disponible en los repos por defecto:

```bash
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev
```

---

# Paso 3 — PostgreSQL

## Crear base de datos y usuario

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE imprint_studio;
CREATE USER imprint_user WITH PASSWORD 'TU_PASSWORD_SEGURO';

ALTER ROLE imprint_user SET client_encoding TO 'utf8';
ALTER ROLE imprint_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE imprint_user SET timezone TO 'America/Mexico_City';

GRANT ALL PRIVILEGES ON DATABASE imprint_studio TO imprint_user;

\q
```

---

# Paso 4 — Clonar el proyecto

```bash
sudo mkdir -p /opt/imprint-studio
sudo chown deploy:deploy /opt/imprint-studio

git clone https://github.com/TU_USUARIO/imprint-studio.git /opt/imprint-studio
cd /opt/imprint-studio
```

---

# Paso 5 — Backend

## Entorno virtual

```bash
cd /opt/imprint-studio/backend
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Variables de entorno

```bash
cp /opt/imprint-studio/.env.example /opt/imprint-studio/backend/.env
```

Editar `/opt/imprint-studio/backend/.env` con valores reales:

```env
# Django
DJANGO_SECRET_KEY=<genera con: python3 -c "import secrets; print(secrets.token_hex(50))">
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com

# Base de datos
USE_SQLITE=false
DB_NAME=imprint_studio
DB_USER=imprint_user
DB_PASSWORD=TU_PASSWORD_SEGURO
DB_HOST=localhost
DB_PORT=5432

# JWT
JWT_ACCESS_MINUTES=60
JWT_REFRESH_DAYS=7

# CORS — solo el dominio del frontend
CORS_ALLOWED_ORIGINS=https://tudominio.com
CSRF_TRUSTED_ORIGINS=https://tudominio.com

# Cloudinary
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret

# Brevo (SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_usuario_brevo
EMAIL_HOST_PASSWORD=tu_api_key_brevo
DEFAULT_FROM_EMAIL=Imprint Studio <noreply@tudominio.com>

# WhatsApp (dejar vacío si aún no se configura)
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_ID=

# Scheduler — activar en producción
SCHEDULER_AUTOSTART=true

# Logging
DJANGO_LOG_LEVEL=WARNING
```

## Migraciones y datos iniciales

```bash
cd /opt/imprint-studio/backend
source venv/bin/activate

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py seed_initial_data
python manage.py createsuperuser
```

## Verificar

```bash
python manage.py check --deploy
```

---

# Paso 6 — Gunicorn (systemd)

## Crear archivo de servicio

```bash
sudo nano /etc/systemd/system/imprint-studio.service
```

Contenido:

```ini
[Unit]
Description=Imprint Studio — Gunicorn
After=network.target postgresql.service

[Service]
User=deploy
Group=deploy
WorkingDirectory=/opt/imprint-studio/backend
EnvironmentFile=/opt/imprint-studio/backend/.env
ExecStart=/opt/imprint-studio/backend/venv/bin/gunicorn config.wsgi:application \
  --workers 3 \
  --threads 2 \
  --worker-class gthread \
  --bind unix:/run/imprint-studio.sock \
  --timeout 120 \
  --access-logfile /var/log/imprint-studio/access.log \
  --error-logfile /var/log/imprint-studio/error.log
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## Crear directorio de logs y socket

```bash
sudo mkdir -p /var/log/imprint-studio
sudo chown deploy:deploy /var/log/imprint-studio

sudo mkdir -p /run
```

## Habilitar e iniciar

```bash
sudo systemctl daemon-reload
sudo systemctl enable imprint-studio
sudo systemctl start imprint-studio
sudo systemctl status imprint-studio
```

---

# Paso 7 — Frontend (build)

En tu máquina local o en el VPS:

```bash
cd /opt/imprint-studio/frontend
# Si Node no está instalado en el VPS:
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

npm ci
npm run build
```

Copiar el build a la ruta que sirve Nginx:

```bash
sudo mkdir -p /var/www/imprint-studio
sudo cp -r /opt/imprint-studio/frontend/dist/* /var/www/imprint-studio/
sudo chown -R www-data:www-data /var/www/imprint-studio
```

---

# Paso 8 — Nginx

## Crear configuración

```bash
sudo nano /etc/nginx/sites-available/imprint-studio
```

Contenido:

```nginx
# Redirigir HTTP a HTTPS
server {
    listen 80;
    server_name tudominio.com www.tudominio.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tudominio.com www.tudominio.com;

    # SSL — Let's Encrypt (certbot los configura automáticamente)
    ssl_certificate /etc/letsencrypt/live/tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tudominio.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # ── Frontend (SPA) ──
    root /var/www/imprint-studio;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # ── API (backend) ──
    location /api/ {
        proxy_pass http://unix:/run/imprint-studio.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 20M;
    }

    # ── Django admin ──
    location /admin/ {
        proxy_pass http://unix:/run/imprint-studio.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # ── Archivos estáticos de Django (admin CSS/JS) ──
    location /static/ {
        alias /opt/imprint-studio/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Seguridad
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;
    gzip_min_length 256;
}
```

## Habilitar el sitio

```bash
sudo ln -s /etc/nginx/sites-available/imprint-studio /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

---

# Paso 9 — SSL con Let's Encrypt

Antes de este paso, el DNS ya debe apuntar al VPS.

```bash
sudo certbot --nginx -d tudominio.com -d www.tudominio.com
```

Certbot modifica la configuración de Nginx automáticamente y configura renovación automática.

Verificar renovación:

```bash
sudo certbot renew --dry-run
```

---

# Paso 10 — Cloudflare DNS

En el panel de Cloudflare:

| Tipo | Nombre | Contenido | Proxy |
|------|--------|-----------|-------|
| A | @ | IP_DEL_VPS | Proxied (naranja) |
| A | www | IP_DEL_VPS | Proxied (naranja) |

Configuración SSL de Cloudflare:

* SSL/TLS → modo **Full (strict)**
* Edge Certificates → Always Use HTTPS: **On**
* Edge Certificates → Minimum TLS Version: **1.2**

---

# Paso 11 — GitHub Secrets (CI/CD)

En GitHub → Settings → Secrets and variables → Actions, crear:

| Secret | Valor |
|--------|-------|
| `VPS_HOST` | IP o dominio del VPS |
| `VPS_USER` | `deploy` |
| `VPS_SSH_KEY` | Clave privada SSH del usuario deploy |

En GitHub → Settings → Environments, crear el environment `production`.

El pipeline `deploy.yml` se activa automáticamente cuando CI pasa en `main`.

---

# Paso 12 — Permisos para deploy automático

El usuario `deploy` necesita reiniciar servicios sin password:

```bash
sudo visudo -f /etc/sudoers.d/deploy
```

Contenido:

```
deploy ALL=(ALL) NOPASSWD: /bin/systemctl restart imprint-studio
deploy ALL=(ALL) NOPASSWD: /bin/systemctl reload nginx
```

---

# Paso 13 — Backups automáticos

## Script de backup

```bash
sudo nano /opt/imprint-studio/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/imprint-studio/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

pg_dump -U imprint_user -h localhost imprint_studio \
  | gzip > "$BACKUP_DIR/db_${TIMESTAMP}.sql.gz"

# Retener solo 30 días
find "$BACKUP_DIR" -name "db_*.sql.gz" -mtime +30 -delete
```

```bash
sudo chmod +x /opt/imprint-studio/backup.sh
```

## Cron (diario a las 3am)

```bash
crontab -e
```

```
0 3 * * * /opt/imprint-studio/backup.sh >> /var/log/imprint-studio/backup.log 2>&1
```

---

# Paso 14 — Rotación de logs

```bash
sudo nano /etc/logrotate.d/imprint-studio
```

```
/var/log/imprint-studio/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    copytruncate
}
```

---

# Paso 15 — Monitoreo

Configurar [UptimeRobot](https://uptimerobot.com) (plan gratuito):

* Monitor tipo HTTP(s)
* URL: `https://tudominio.com/api/v1/admin/dashboard/` (o cualquier endpoint de health)
* Intervalo: 5 minutos
* Alerta: email

---

# Checklist post-deploy

```
[ ] HTTPS funciona (candado verde)
[ ] https://tudominio.com carga el frontend
[ ] https://tudominio.com/api/v1/auth/register/ responde 400 (sin datos)
[ ] https://tudominio.com/admin/ carga Django admin
[ ] Registro + OTP funciona
[ ] Crear pedido funciona
[ ] Subir archivo funciona
[ ] Dashboard admin carga métricas
[ ] Backup manual ejecuta sin error
[ ] UptimeRobot reporta UP
[ ] GitHub Actions deploy ejecuta correctamente
```

---

# Comandos útiles de operación

```bash
# Ver logs de la app
sudo journalctl -u imprint-studio -f

# Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log

# Reiniciar backend
sudo systemctl restart imprint-studio

# Recargar Nginx (sin downtime)
sudo systemctl reload nginx

# Entrar al shell de Django
cd /opt/imprint-studio/backend
source venv/bin/activate
python manage.py shell

# Backup manual
/opt/imprint-studio/backup.sh

# Renovar SSL manualmente
sudo certbot renew
```

---

# Diagrama de flujo final

```
Internet
   ↓
Cloudflare (DNS + CDN + SSL edge)
   ↓
VPS :443
   ↓
Nginx
   ├── /              → /var/www/imprint-studio/ (Vue SPA)
   ├── /api/           → unix:/run/imprint-studio.sock (Gunicorn → Django)
   ├── /admin/         → unix:/run/imprint-studio.sock (Gunicorn → Django)
   └── /static/        → /opt/imprint-studio/backend/staticfiles/
```

---

# Estado del documento

Versión: 1.0

Fuente oficial para la configuración inicial del VPS de producción.
