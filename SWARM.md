# Развертывание с Docker Swarm

> **Примечание:** Все команды в данной документации описаны для окружения Ubuntu 22.04. Для других операционных систем команды могут отличаться.

## Требования

Перед запуском приложения необходимо установить следующие компоненты:

1. **Docker**
2. **Python 3** (для нагрузочного тестирования)

## Развертывание с 4 репликами Flask приложения

### Конфигурация Docker Swarm

Файл `docker-compose.swarm.yml` содержит конфигурацию для развертывания с использованием Swarm:

- 4 реплики Flask приложения
- 1 реплика Redis
- Встроенная балансировка нагрузки

### Команды для развертывания

```bash
# Инициализация Swarm
docker swarm init

# Сборка образа
docker build -t localhost:5000/counter-app:latest .

# Развертывание стека
docker stack deploy -c docker-compose.swarm.yml counter

# Проверка статуса сервисов
docker stack services counter

# Просмотр реплик
docker service ps counter_app
docker service ps counter_redis

# Масштабирование сервиса (изменить количество реплик)
docker service scale counter_app=1
docker service scale counter_app=4
```

### Остановка и удаление стека

```bash
# Удаление стека (остановит все сервисы и удалит стек)
docker stack rm counter

# Ожидание полного удаления стека (проверка статуса)
docker stack services counter

# Удаление неиспользуемых сетей
docker network prune -f

# Полная остановка Swarm (после удаления всех стеков)
docker swarm leave --force
```

> **Примечание:** Если порт 80 уже занят другим стеком, необходимо сначала удалить предыдущий стек командой `docker stack rm <имя_стека>`.

### Доступ к приложению

После успешного развертывания приложение будет доступно по адресу:

- **http://localhost**

Приложение использует порт **80** для внешнего доступа. Балансировщик нагрузки Docker Swarm автоматически распределяет запросы между 4 репликами Flask приложения.

## Развертывание с реплицированной БД (Redis)

### Конфигурация с несколькими репликами Redis

Файл `docker-compose.swarm-replicated.yml` содержит конфигурацию с **3 репликами Redis**

### Особенности работы с реплицированной БД

> **Примечание:** Текущая конфигурация `docker-compose.swarm-replicated.yml` демонстрирует развертывание нескольких реплик, но без синхронизации данных.

### Команды для развертывания с реплицированной БД

```bash
# Инициализация Swarm
docker swarm init

# Сборка образа
docker build -t localhost:5000/counter-app:latest .

# Развертывание стека с реплицированной БД
docker stack deploy -c docker-compose.swarm-replicated.yml counter-replicated

# Проверка статуса сервисов
docker stack services counter-replicated

# Просмотр реплик
docker service ps counter-replicated_app
docker service ps counter-replicated_redis
```

### Остановка и удаление стека

```bash
# Удаление стека (остановит все сервисы и удалит стек)
docker stack rm counter-replicated

# Ожидание полного удаления стека (проверка статуса)
docker stack services counter-replicated

# Удаление неиспользуемых сетей (опционально)
docker network prune -f

# Полная остановка Swarm (после удаления всех стеков)
docker swarm leave --force
```

> **Примечание:** Если порт 80 уже занят другим стеком, необходимо сначала удалить предыдущий стек командой `docker stack rm <имя_стека>`.

## Нагрузочное тестирование

Для проверки производительности приложения с 4 репликами используется Locust.

### Установка Locust

Рекомендуется использовать виртуальное окружение для избежания конфликтов зависимостей:

```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация виртуального окружения
source venv/bin/activate

# Установка Locust
pip install locust
```

Для деактивации виртуального окружения используйте:
```bash
deactivate
```

### Запуск нагрузочного тестирования

После активации виртуального окружения:

```bash
# Запуск Locust с веб-интерфейсом (по умолчанию http://localhost:8089)
locust --host=http://localhost

# Запуск без веб-интерфейса (headless режим) для автоматизированного тестирования
locust --host=http://localhost --headless -u 300 -r 30 -t 60s

# Где:
# -u 300 - 300 пользователей (виртуальных клиентов)
# -r 30  - скорость набора пользователей (30 в секунду)
# -t 60s - длительность теста (60 секунд)
```

### Веб-интерфейс Locust

После запуска `locust --host=http://localhost` откройте в браузере:

- **http://localhost:8089**