#  System Update Procedure

Дотримуйтесь цих кроків для оновлення системи до нової версії:

1. **Зупинка сервісу:** `sudo systemctl stop it_support`
2. **Оновлення коду:**
   Bash
   git pull origin main
   source venv/bin/activate
   pip install -r requirements.txt

3. **Міграції БД:**
 Виконайте скрипти оновлення схем (якщо є зміни в моделях SQLAlchemy).

4. **Запуск та перевірка:**

Bash
sudo systemctl start it_support
journalctl -u it_support -f  # Перегляд логів на помилки