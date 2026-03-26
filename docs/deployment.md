# Production Deployment Guide

##  Системні вимоги
- **OS:** Windows 10 (рекомендується).
- **Resources:** 1 CPU, 2GB RAM, 10GB SSD.

##  Стек розгортання
- **Web-server:** Nginx (Reverse Proxy).
- **WSGI/ASGI:** Gunicorn з воркерами Uvicorn.
- **Process Manager:** Systemd.

##  Кроки розгортання
1. **Налаштування Systemd:** Створіть сервіс `/etc/systemd/system/it_support.service`.
2. **Nginx:** Налаштуйте проксіювання запитів з порту 80/443 на внутрішній порт 8000.
3. **Security:** Ввімкніть `ufw` фаєрвол, дозволивши лише порти 80, 443 та 22 (SSH).