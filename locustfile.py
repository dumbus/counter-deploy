from locust import HttpUser, task, between, events


class CounterUser(HttpUser):
    """Виртуальный пользователь для нагрузочного тестирования приложения счетчика"""
    
    wait_time = between(0.5, 2)

    def on_start(self):
        """Инициализация: загрузка главной страницы при старте пользователя"""
        self.client.get("/")

    @task(15)
    def get_counter(self):
        """Получение текущего значения счетчика (наиболее частый запрос)"""
        with self.client.get("/api/counter", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "value" in data:
                        response.success()
                    else:
                        response.failure("Неверный формат ответа")
                except ValueError:
                    response.failure("Неверный формат ответа")
            else:
                response.failure("Ошибка HTTP")

    @task(7)
    def increment_counter(self):
        """Увеличение значения счетчика"""
        with self.client.post("/api/counter/increment", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "value" in data:
                        response.success()
                    else:
                        response.failure("Неверный формат ответа")
                except ValueError:
                    response.failure("Неверный формат ответа")
            else:
                response.failure("Ошибка HTTP")

    @task(4)
    def decrement_counter(self):
        """Уменьшение значения счетчика"""
        with self.client.post("/api/counter/decrement", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "value" in data:
                        response.success()
                    else:
                        response.failure("Неверный формат ответа")
                except ValueError:
                    response.failure("Неверный формат ответа")
            else:
                response.failure("Ошибка HTTP")

    @task(3)
    def load_main_page(self):
        """Загрузка главной страницы приложения"""
        self.client.get("/")

    @task(1)
    def reset_counter(self):
        """Сброс счетчика в начальное значение (наименее частый запрос)"""
        self.client.post("/api/counter/reset")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Вывод статистики после завершения теста"""
    print("Статистика тестирования")

    stats = environment.stats
    print(f"Всего запросов: {stats.total.num_requests}")
    print(f"Количество ошибок: {stats.total.num_failures}")
    print(f"Среднее время отклика: {stats.total.avg_response_time:.2f} мс")
    print(f"Медианное время отклика: {stats.total.median_response_time:.2f} мс")
    print(f"95-й перцентиль: {stats.total.get_response_time_percentile(0.95):.2f} мс")
    print(f"99-й перцентиль: {stats.total.get_response_time_percentile(0.99):.2f} мс")
    print(f"Запросов в секунду (RPS): {stats.total.total_rps:.2f}")