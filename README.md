# counter-deploy
Пример проекта для деплоя приложения счетчик на сервер

## Развертывание с 4 репликами Flask приложения

### Конфигурация Docker Swarm

Файл `docker-compose.swarm.yml` содержит конфигурацию для кластеризованного развертывания:

- 4 реплики Flask приложения
- Встроенная балансировка нагрузки

### Команды для развертывания

```bash
# Инициализация Swarm (если еще не инициализирован)
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

# Масштабирование (если нужно изменить количество реплик)
docker service scale counter_app=4

# Удаление стека
docker stack rm counter
```

### Доступ к приложению

После успешного развертывания приложение будет доступно по адресу:

- **http://localhost**

Приложение использует порт **80** для внешнего доступа. Балансировщик нагрузки Docker Swarm автоматически распределяет запросы между 4 репликами Flask приложения.
