# Деплой Visa Centrum XBA на VPS

Текущий `Dockerfile`/`compose.yaml` — для разработки (голый `runserver`, SQLite без volume для media, нет HTTPS). Ниже — полный план с нужными доработками для продакшена.

## 0. Что нужно доработать перед деплоем

**`requirements.txt`** — добавить:
```
gunicorn==23.0.0
whitenoise==6.8.2
```

**`visa_centrum/settings.py`** — добавить WhiteNoise и путь для собранной статики:
```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # сразу после SecurityMiddleware
    ...
]

STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
```

**`Dockerfile`** — продакшн-версия (gunicorn вместо `runserver`, collectstatic на старте):
```dockerfile
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn visa_centrum.wsgi:application --bind 0.0.0.0:8001 --workers 3"]
```

Сделай эти изменения локально, закоммить (`git init && git add . && git commit -m "prod setup"` — проект сейчас не git-репозиторий), и запушь в приватный GitHub/GitLab репозиторий — так проще всего доставлять код на сервер и обновлять его.

## 1. Выбор и подготовка VPS

- Минимум: 1 vCPU, 1–2 GB RAM, 20 GB SSD (Hetzner CX22, DigitalOcean Basic, Timeweb/VK Cloud и т.п. — сайт лёгкий, SQLite, большой нагрузки не будет).
- ОС: Ubuntu 22.04/24.04 LTS.
- Привяжи домен: в DNS-зоне домена создай **A-запись**, указывающую на IP VPS (например `visacentrum.uz → 123.45.67.89`, и при желании `www` тоже).

## 2. Первичная настройка сервера

Подключись как root:
```bash
ssh root@ВАШ_IP
```

Создай обычного пользователя с sudo (не работать под root):
```bash
adduser deploy
usermod -aG sudo deploy
rsync --archive --chown=deploy:deploy ~/.ssh /home/deploy
```

Зайди под новым пользователем в отдельной сессии и проверь, что вход по ключу работает, затем на root-сессии отключи пароль/root-вход:
```bash
sudo nano /etc/ssh/sshd_config
# PermitRootLogin no
# PasswordAuthentication no
sudo systemctl restart ssh
```

Настрой файрвол:
```bash
sudo ufw allow OpenSSH
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

(Опционально) fail2ban против брутфорса по SSH:
```bash
sudo apt update && sudo apt install -y fail2ban
```

## 3. Установка Docker

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker deploy
# перелогиниться, чтобы группа применилась
```

Проверь: `docker --version` и `docker compose version`.

## 4. Доставка кода на сервер

```bash
sudo mkdir -p /opt/visa_centrum_web
sudo chown deploy:deploy /opt/visa_centrum_web
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ> /opt/visa_centrum_web
cd /opt/visa_centrum_web
```

Если без git — `rsync -avz --exclude='.venv' --exclude='db.sqlite3' ./ deploy@ВАШ_IP:/opt/visa_centrum_web/` с локальной машины.

## 5. `.env` для продакшена

```bash
cd /opt/visa_centrum_web
nano .env
```
```ini
DJANGO_SECRET_KEY=<сгенерировать ниже>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=visacentrum.uz,www.visacentrum.uz
DJANGO_CSRF_TRUSTED_ORIGINS=https://visacentrum.uz,https://www.visacentrum.uz
```

Сгенерировать реальный `SECRET_KEY`:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || \
docker run --rm python:3.13-slim python -c "import secrets; print(secrets.token_urlsafe(50))"
```

## 6. Продакшн `compose.yaml` с reverse-proxy и HTTPS

Проще всего взять **Caddy** — сам получает и обновляет Let's Encrypt сертификат, без отдельного certbot.

```yaml
services:
  web:
    build:
      context: .
    expose:
      - "8001"
    env_file: .env
    volumes:
      - ./db.sqlite3:/app/db.sqlite3
      - static_data:/app/staticfiles
    restart: unless-stopped

  caddy:
    image: caddy:2-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      - web
    restart: unless-stopped

volumes:
  static_data:
  caddy_data:
  caddy_config:
```

`Caddyfile` (в корне проекта):
```
visacentrum.uz, www.visacentrum.uz {
    reverse_proxy web:8001
}
```

Caddy сам выпустит и будет продлевать HTTPS-сертификат — никакого отдельного certbot не нужно.

## 7. Запуск

```bash
cd /opt/visa_centrum_web
touch db.sqlite3
docker compose up -d --build
docker compose logs -f web   # проверить, что migrate/collectstatic прошли без ошибок
```

Создать суперпользователя (интерактивно, чтобы пароль не улетал в историю команд/логи):
```bash
docker compose exec -it web python manage.py createsuperuser
```

Проверь:
```bash
curl -I https://visacentrum.uz/
curl -I https://visacentrum.uz/admin/login/
```

## 8. Автозапуск после перезагрузки сервера

`restart: unless-stopped` в compose уже переживает `docker` restart; дополнительно включи сам Docker-демон в автозагрузку (обычно уже включён `get.docker.com`-инсталлятором):
```bash
sudo systemctl enable docker
```

## 9. Бэкапы

Простой cron для ежедневного бэкапа базы и статики:
```bash
crontab -e
```
```
0 3 * * * cp /opt/visa_centrum_web/db.sqlite3 /opt/backups/db_$(date +%F).sqlite3
```
(создай `/opt/backups` заранее, и не забудь ротацию/выгрузку бэкапов куда-то вне сервера — например, по rsync на другую машину или в облачное хранилище.)

## 10. Админка на отдельном поддомене

Админка уже вынесена из `i18n_patterns` на отдельный путь `/admin/` (`visa_centrum/urls.py`), поэтому это один и тот же Django-процесс — просто два hostname указывают на него через Caddy.

**DNS:** добавь ещё одну A-запись — `admin.visacentrum.uz → тот же IP VPS`.

**`.env`:**
```ini
DJANGO_ALLOWED_HOSTS=visacentrum.uz,www.visacentrum.uz,admin.visacentrum.uz
DJANGO_CSRF_TRUSTED_ORIGINS=https://visacentrum.uz,https://www.visacentrum.uz,https://admin.visacentrum.uz
```

**`Caddyfile`** — два варианта:

**Вариант 1 (проще): `admin.visacentrum.uz/admin/`**
```
visacentrum.uz, www.visacentrum.uz {
    reverse_proxy web:8001
}

admin.visacentrum.uz {
    reverse_proxy web:8001
}
```
Заходишь на `https://admin.visacentrum.uz/admin/` — путь `/admin/` всё равно нужен, но он теперь на отдельном домене/сертификате.

**Вариант 2 (чище): `admin.visacentrum.uz/` сразу без `/admin/` в пути**
```
visacentrum.uz, www.visacentrum.uz {
    reverse_proxy web:8001
}

admin.visacentrum.uz {
    rewrite * /admin{uri}
    reverse_proxy web:8001
}
```
Тогда просто `https://admin.visacentrum.uz/` ведёт прямо в админку.

**(Опционально, для безопасности)** — закрыть `/admin/` на основном домене, чтобы админка отвечала только по поддомену:
```
visacentrum.uz, www.visacentrum.uz {
    @admin path /admin* /static/admin*
    respond @admin 404
    reverse_proxy web:8001
}
```
(не забудь исключение для `/static/admin*`, иначе сломается CSS/JS самой админки, если открываешь её напрямую на основном домене.)

## 11. Обновление проекта после правок кода

```bash
cd /opt/visa_centrum_web
git pull
docker compose up -d --build
```

## Итоговый чек-лист перед тем, как объявлять сайт "в проде"

- [ ] `DJANGO_DEBUG=False`, реальный `SECRET_KEY`, точный `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` под ваш домен
- [ ] HTTPS работает (Caddy сам выпустил сертификат)
- [ ] Суперпользователь создан, вход в `/admin/` работает
- [ ] `.env` и `db.sqlite3` не закоммичены в git (проверь `.gitignore`)
- [ ] Бэкап базы настроен
- [ ] UFW включён, SSH только по ключу
