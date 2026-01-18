# Развертывание с Kubernetes (k3s)

> **Примечание:** Все команды в данной документации описаны для окружения Ubuntu 22.04. Для других операционных систем команды могут отличаться.

## Требования

Перед запуском приложения необходимо установить следующие компоненты:

1. **Docker**
2. **Python 3**
3. **kubectl**
4. **k3s**

## Конфигурация для k3s

Файл `k8s-deployment.yaml` содержит конфигурацию для развертывания с использованием Kubernetes/k3s:

- 4 реплики Flask приложения
- 1 реплика Redis
- Service для балансировки нагрузки приложения (LoadBalancer на порту 80)
- Service для Redis (ClusterIP на порту 6379)

## Команды для развертывания с k3s

```bash
# Сборка образа
docker build -t localhost:5000/counter-app:latest .

# Экспорт образа Docker в tar файл для импорта в k3s
docker save localhost:5000/counter-app:latest -o counter-app.tar

# Импорт образа в k3s
sudo k3s ctr images import counter-app.tar

# Развертывание в Kubernetes
sudo kubectl apply -f k8s-deployment.yaml

# Проверка статуса развертывания
sudo kubectl get deployments
sudo kubectl get pods
sudo kubectl get services

# Если поды не запускаются, проверьте статус подов приложения:
sudo kubectl describe pods -l app=counter-app

# Просмотр логов приложения
sudo kubectl logs -f deployment/counter-app

# Масштабирование приложения (изменить количество реплик)
sudo kubectl scale deployment counter-app --replicas=1
sudo kubectl scale deployment counter-app --replicas=4

# Проверка статуса подов
sudo kubectl get pods -l app=counter-app
```

> **Примечание:** В k3s команды `kubectl` требуют `sudo` или настройки прав доступа к конфигурационному файлу. В данной документации все команды `kubectl` выполняются с `sudo`. Альтернативно можно настроить права доступа к конфигурационному файлу: `sudo chmod 644 /etc/rancher/k3s/k3s.yaml` и использовать команды без `sudo`.

## Доступ к приложению в k3s

После развертывания приложение будет доступно через LoadBalancer service. В k3s LoadBalancer автоматически пробрасывает порт на localhost:

```bash
# Получение информации о сервисе (проверка порта)
sudo kubectl get service counter-app-service
```

Приложение будет доступно по адресу: **http://localhost**

> **Примечание:** k3s автоматически пробрасывает LoadBalancer сервисы на localhost, поэтому после развертывания приложение сразу доступно по `http://localhost` без дополнительных настроек. Если LoadBalancer не работает локально, можно использовать `sudo kubectl port-forward service/counter-app-service 80:80`.

## Остановка и удаление развертывания

```bash
# Удаление всех ресурсов из манифеста
sudo kubectl delete -f k8s-deployment.yaml

# Или удаление отдельных ресурсов
sudo kubectl delete deployment counter-app
sudo kubectl delete deployment redis
sudo kubectl delete service counter-app-service
sudo kubectl delete service redis-service

# Проверка удаления
sudo kubectl get all

# Остановка k3s (опционально)
sudo systemctl stop k3s
sudo systemctl disable k3s
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