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

# Масштабирование сервиса (изменить количество реплик без редактирования файла)
docker service scale counter_app=1  # Уменьшить до 1 реплики
docker service scale counter_app=4  # Увеличить до 4 реплик
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

**Примечание:** Если порт 80 уже занят другим стеком, необходимо сначала удалить предыдущий стек командой `docker stack rm <имя_стека>`.

### Доступ к приложению

После успешного развертывания приложение будет доступно по адресу:

- **http://localhost**

Приложение использует порт **80** для внешнего доступа. Балансировщик нагрузки Docker Swarm автоматически распределяет запросы между 4 репликами Flask приложения.

## Развертывание с реплицированной БД (Redis)

### Конфигурация с несколькими репликами Redis

Файл `docker-compose.swarm-replicated.yml` содержит конфигурацию с **3 репликами Redis** для повышения отказоустойчивости.

### Особенности работы с реплицированной БД

**Важно:** При использовании нескольких реплик Redis в Docker Swarm с настройкой по умолчанию возникают следующие особенности:

1. **Независимые экземпляры БД**
   - Каждая реплика Redis является независимым экземпляром
   - Данные **не синхронизируются** автоматически между репликами
   - Каждое подключение может попасть на любой экземпляр Redis

2. **Проблема консистентности данных**
   - Запись в одну реплику не отражается в других
   - Разные экземпляры приложения могут видеть разные данные
   - Потеря целостности данных счетчика

3. **Балансировка подключений**
   - Docker Swarm распределяет подключения между репликами случайным образом
   - Нет контроля, какое приложение к какой реплике подключается

### Пути решения проблем репликации

Для корректной работы с несколькими репликами Redis необходимо выбрать один из подходов:

1. **Redis Sentinel**
   - Автоматическое управление master и replicas
   - Автоматический failover при отказе master
   - Требует дополнительной настройки конфигурации

2. **Redis Cluster**
   - Распределение данных по нескольким узлам
   - Автоматическая репликация
   - Более сложная настройка, но лучшая производительность

3. **Внешний managed Redis** (AWS ElastiCache, Redis Cloud и т.д.)
   - Управляемый сервис с автоматической репликацией
   - Минимальная настройка, максимальная надежность

**Примечание:** Текущая конфигурация `docker-compose.swarm-replicated.yml` демонстрирует развертывание нескольких реплик, но без синхронизации данных.

### Команды для развертывания с реплицированной БД

```bash
# Инициализация Swarm (если еще не инициализирован)
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

**Примечание:** Если порт 80 уже занят другим стеком, необходимо сначала удалить предыдущий стек командой `docker stack rm <имя_стека>`.

## Развертывание с Kubernetes (k3s)

### Kubernetes vs Docker Swarm

При использовании Kubernetes вместо Docker Swarm происходят следующие изменения:

1. **Формат конфигурации**
   - Swarm использует `docker-compose.yml` с синтаксисом Compose
   - Kubernetes использует YAML-манифесты с декларативным API Kubernetes

2. **Архитектура**
   - Swarm интегрирован в Docker, более простая настройка
   - Kubernetes - отдельная оркестрационная система, более мощная, но сложнее

3. **Балансировка нагрузки**
   - Swarm: встроенная балансировка через VIP (Virtual IP)
   - Kubernetes: Service с типами ClusterIP, NodePort, LoadBalancer

4. **Масштабирование**
   - Swarm: `docker service scale`
   - Kubernetes: `kubectl scale deployment` или изменение `replicas` в манифесте

### Конфигурация для k3s

Файл `k8s-deployment.yaml` содержит конфигурацию для развертывания в Kubernetes/k3s:

- 4 реплики Flask приложения (Deployment)
- 1 реплика Redis (Deployment)
- Service для балансировки нагрузки приложения (LoadBalancer на порту 80)
- Service для Redis (ClusterIP на порту 6379)

### Команды для развертывания с k3s

```bash
# Сборка образа
docker build -t localhost:5000/counter-app:latest .

# Экспорт образа Docker в tar файл для импорта в k3s
docker save localhost:5000/counter-app:latest -o counter-app.tar

# Импорт образа в k3s
sudo k3s ctr images import counter-app.tar

# Развертывание в Kubernetes
kubectl apply -f k8s-deployment.yaml

# Проверка статуса развертывания
kubectl get deployments
kubectl get pods
kubectl get services

# Если поды не запускаются, проверьте статус подов приложения:
kubectl describe pods -l app=counter-app

# Просмотр логов приложения
kubectl logs -f deployment/counter-app

# Масштабирование приложения (изменить количество реплик)
kubectl scale deployment counter-app --replicas=4
kubectl scale deployment counter-app --replicas=1

# Проверка статуса подов
kubectl get pods -l app=counter-app
```

**Примечание:** В k3s команды `kubectl` могут требовать `sudo` или настройки прав доступа к конфигурационному файлу. Если возникают ошибки с правами доступа, используйте `sudo` перед командами `kubectl` или выполните `sudo chmod 644 /etc/rancher/k3s/k3s.yaml` для настройки прав.

### Доступ к приложению в k3s

После развертывания приложение будет доступно через LoadBalancer service. В k3s LoadBalancer автоматически пробрасывает порт на localhost:

```bash
# Получение информации о сервисе (проверка порта)
kubectl get service counter-app-service
```

Приложение будет доступно по адресу: **http://localhost**

**Примечание:** k3s автоматически пробрасывает LoadBalancer сервисы на localhost, поэтому после развертывания приложение сразу доступно по `http://localhost` без дополнительных настроек. Если LoadBalancer не работает локально, можно использовать `kubectl port-forward service/counter-app-service 80:80`.

### Остановка и удаление развертывания

```bash
# Удаление всех ресурсов из манифеста
kubectl delete -f k8s-deployment.yaml

# Или удаление отдельных ресурсов
kubectl delete deployment counter-app
kubectl delete deployment redis
kubectl delete service counter-app-service
kubectl delete service redis-service

# Проверка удаления
kubectl get all

# Остановка k3s (опционально)
sudo systemctl stop k3s
sudo systemctl disable k3s
```

### Нагрузочное тестирование с k3s

После развертывания приложения в k3s, нагрузочное тестирование проводится аналогично Swarm:

```bash
# Активация виртуального окружения (если еще не активировано)
source venv/bin/activate

# Нагрузочное тестирование через LoadBalancer или port-forward
locust --host=http://localhost --headless -u 300 -r 30 -t 60s

# Или с веб-интерфейсом
locust --host=http://localhost
```

**Сравнение с разным количеством реплик:**

**Тест с 1 репликой**

```bash
kubectl scale deployment counter-app --replicas=1
locust --host=http://localhost --headless -u 300 -r 30 -t 60s
```

**Тест с 4 репликами**

```bash
kubectl scale deployment counter-app --replicas=4
locust --host=http://localhost --headless -u 300 -r 30 -t 60s
```

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

В веб-интерфейсе можно:
- Указать количество пользователей
- Указать скорость набора пользователей
- Запустить тест и наблюдать статистику в реальном времени
- Экспортировать отчеты

### Сравнение производительности

Для сравнения производительности можно использовать команду масштабирования:

**Тест с 1 репликой**

```bash
docker service scale counter_app=1
locust --host=http://localhost --headless -u 300 -r 30 -t 60s
```

**Тест с 4 репликами**

```bash
docker service scale counter_app=4
locust --host=http://localhost --headless -u 300 -r 30 -t 60s
```