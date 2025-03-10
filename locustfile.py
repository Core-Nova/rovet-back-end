from locust import HttpUser, task, between
from app.core.config import settings


class APIUser(HttpUser):
    wait_time = between(1, 3)
    token = None

    def on_start(self):
        # Login and get token
        response = self.client.post(
            f"{settings.API_V1_STR}/auth/login",
            data={"username": "test@example.com", "password": "test123"}
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]

    @task(1)
    def health_check(self):
        self.client.get(f"{settings.API_V1_STR}/health")

    @task(2)
    def get_current_user(self):
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.get(f"{settings.API_V1_STR}/auth/me", headers=headers)

    @task(1)
    def register_user(self):
        import random
        email = f"user{random.randint(1, 100000)}@example.com"
        self.client.post(
            f"{settings.API_V1_STR}/auth/register",
            json={
                "email": email,
                "password": "test123",
                "full_name": "Test User"
            }
        ) 