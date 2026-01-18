# Масштабирование приложений (Отчёт)

> Дисциплина "Проектирование и развертывание веб-решений в эко-системе Python"

## Docker registry for Linux Part 1

1. Содержимое registry:

<img width="1112" height="804" alt="1" src="https://github.com/user-attachments/assets/e8c41e39-15e9-4b48-9cb7-f34ae0d7a944" />

## Docker registry for Linux Parts 2 & 3

1. Успешная аутентификация

<img width="815" height="51" alt="2 1" src="https://github.com/user-attachments/assets/0c2f9775-883a-4247-a144-6b4f4f6c1288" />

2. Неуспешная аутентификация

<img width="981" height="62" alt="2 2" src="https://github.com/user-attachments/assets/63396e0e-483a-4b48-9404-1ca72883c2d8" />

## Docker Orchestration Hands-on Lab

1. Узлы в состоянии **Active**

<img width="475" height="84" alt="3" src="https://github.com/user-attachments/assets/5af7bc74-fac1-49fc-be5f-b98aa0056fbf" />

2. Узлы в состоянии **Drain**

<img width="472" height="88" alt="4" src="https://github.com/user-attachments/assets/94c37684-c560-4538-9582-9d58ececd780" />

### Восстановилась ли работа запущенного сервиса на этом узле после перевода из Drain в Active?

Нет, автоматического восстановления работы не происходит.  
Когда узел переводится в режим Drain, Docker Swarm останавливает все задачи на этом узле и перемещает их на другие доступные узлы кластера. После возврата узла в режим Active он снова становится доступным для планировщика Swarm и может принимать новые задачи, но ранее перемещённые задачи на него автоматически не возвращаются.

### Что необходимо сделать, чтобы запустить работу службы на этом узле снова?

1. Принудительное обновление сервиса:

```
docker service update --force sleep-app
```

2. Масштабирование сервиса:

```
docker service scale sleep-app=N
```

Где N — новое количество реплик.

## Swarm stack introduction

### Как конфигурируется количество нодов (реплик) в стэке?

Количество нодов (реплик) для каждого сервиса в стеке задаётся через параметр replicas в секции deploy `docker-compose.yml` файла.

```
vote:
  # ...
  deploy:
    replicas: 2
worker:
  # ...
  deploy:
    replicas: 2
```

Docker Swarm запустит:

- 2 реплики сервиса `vote`
- 2 реплики сервиса `worker`

### Как организуется проверка жизнеспособности сервисов в docker-compose.yml?

1. Прямая проверка жизнеспособности через `healthcheck`
2. Зависимости между сервисами с условием готовности (`depends_on` -> `service_healthy`)

## Документация

Проект поддерживает два способа кластеризованного развертывания:

- **[SWARM.md](SWARM.md)** - Развертывание с использованием Docker Swarm
- **[K3S.md](K3S.md)** - Развертывание с использованием Kubernetes (k3s)
