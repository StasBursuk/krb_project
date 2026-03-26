# Backup & Recovery Policy

## Резервне копіювання БД (PostgreSQL)
Використовуйте утиліту `pg_dump` для створення щоденних бекапів:
Bash
pg_dump -U postgres it_support > /backups/db_$(date +%Y%m%d).sql
## Резервне копіювання медіа-файлів
Копіюйте вміст папки backend/static/reports/ (скріншоти помилок) у хмарне сховище або на окремий диск раз на тиждень.

## Відновлення (Recovery)
Bash
psql -U postgres it_support < /backups/db_backup_file.sql