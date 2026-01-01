# Настройка PostgreSQL для продакшена

## 1. Использование postgresql.conf в Docker

### Способ 1: Монтирование файла (рекомендуется)

```bash
# Скопируйте пример конфига
cp postgresql.conf.example postgresql.conf

# Запустите контейнер с монтированием конфига
docker run -d \
  -v $(pwd)/postgresql.conf:/etc/postgresql/postgresql.conf:ro \
  -v postgres_data:/var/lib/postgresql/data \
  --name postgres \
  hajj-umrah-postgres \
  postgres -c config_file=/etc/postgresql/postgresql.conf
```

### Способ 2: Через переменные окружения

PostgreSQL автоматически применяет переменные окружения вида `POSTGRES_*_CONFIG`:

```bash
docker run -d \
  -e POSTGRES_SHARED_BUFFERS=256MB \
  -e POSTGRES_MAX_CONNECTIONS=200 \
  --name postgres \
  hajj-umrah-postgres
```

### Способ 3: Через docker-compose

См. файл `docker-compose.postgres.example.yml` - там показан пример монтирования конфига.

### Как это работает?

- При старте контейнера PostgreSQL ищет конфиг в `/etc/postgresql/postgresql.conf`
- Если файл смонтирован, он используется вместо дефолтного
- Можно комбинировать: базовый конфиг + переменные окружения для переопределения

---

## 2. Расширения для мониторинга PostgreSQL

### Встроенные расширения (уже есть в образе):

#### `pg_stat_statements` - **САМОЕ ВАЖНОЕ**
**Что мониторит:**
- Статистику выполнения всех SQL-запросов
- Время выполнения каждого запроса
- Количество вызовов
- Общее время выполнения
- Использование памяти

**Как использовать:**
```sql
-- Включить расширение в БД
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Посмотреть топ-10 самых медленных запросов
SELECT 
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

#### `pg_buffercache` - мониторинг кэша
**Что мониторит:**
- Что находится в shared buffer cache
- Какие таблицы/индексы кэшируются
- Эффективность использования памяти

**Как использовать:**
```sql
CREATE EXTENSION IF NOT EXISTS pg_buffercache;

-- Посмотреть, что в кэше
SELECT 
    c.relname,
    count(*) AS buffers
FROM pg_buffercache b
INNER JOIN pg_class c ON b.relfilenode = pg_relation_filenode(c.oid)
GROUP BY c.relname
ORDER BY buffers DESC;
```

#### `pg_stat_activity` - активные подключения
**Что мониторит:**
- Текущие подключения к БД
- Активные запросы
- Блокировки
- Долгие транзакции

**Как использовать:**
```sql
-- Посмотреть активные запросы
SELECT 
    pid,
    usename,
    application_name,
    state,
    query,
    query_start,
    now() - query_start AS duration
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;
```

### Дополнительные расширения (требуют установки):

- **pgAudit** - аудит всех операций
- **pgBadger** - анализ логов
- **TimescaleDB** - для временных рядов (если нужно)

---

## 3. Использование pg_dump

**Да, `pg_dump` уже включен в стандартный образ PostgreSQL!** Не нужно ничего дополнительно устанавливать.

### Примеры использования:

#### Бэкап одной БД:
```bash
# Из контейнера
docker exec postgres pg_dump -U postgres hajj_umrah > backup.sql

# Или подключившись к контейнеру
docker exec -it postgres bash
pg_dump -U postgres hajj_umrah > /backups/backup_$(date +%Y%m%d).sql
```

#### Бэкап всех БД:
```bash
docker exec postgres pg_dumpall -U postgres > backup_all.sql
```

#### Бэкап с сжатием:
```bash
docker exec postgres pg_dump -U postgres -Fc hajj_umrah > backup.dump
```

#### Восстановление:
```bash
# Из SQL файла
docker exec -i postgres psql -U postgres hajj_umrah < backup.sql

# Из сжатого дампа
docker exec -i postgres pg_restore -U postgres -d hajj_umrah < backup.dump
```

#### Автоматический бэкап (cron скрипт):
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
CONTAINER_NAME="postgres"
DB_NAME="hajj_umrah"
DB_USER="postgres"

docker exec $CONTAINER_NAME pg_dump -U $DB_USER -Fc $DB_NAME > \
  $BACKUP_DIR/backup_${DATE}.dump

# Удалить бэкапы старше 7 дней
find $BACKUP_DIR -name "backup_*.dump" -mtime +7 -delete
```

### Важно для продакшена:

1. **Регулярные бэкапы**: настройте cron или используйте систему оркестрации (Kubernetes CronJob)
2. **Тестирование восстановления**: периодически проверяйте, что бэкапы восстанавливаются
3. **Хранение**: храните бэкапы не только на том же сервере, но и в другом месте (S3, другой сервер)
4. **Версионирование**: храните несколько версий бэкапов (последние 7 дней ежедневно, последние 4 недели еженедельно)

---

## Быстрый старт

1. **Соберите образ:**
   ```bash
   docker build -f postgres.Dockerfile -t hajj-umrah-postgres .
   ```

2. **Создайте конфиг (опционально):**
   ```bash
   cp postgresql.conf.example postgresql.conf
   # Отредактируйте под свои нужды
   ```

3. **Запустите через docker-compose:**
   ```bash
   docker-compose -f docker-compose.postgres.example.yml up -d
   ```

4. **Включите расширения мониторинга:**
   ```bash
   docker exec -it postgres psql -U postgres -d hajj_umrah
   ```
   ```sql
   CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
   CREATE EXTENSION IF NOT EXISTS pg_buffercache;
   ```


