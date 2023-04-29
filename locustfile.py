from locust import HttpUser, task, between
import random


class User(HttpUser):
    wait_time = between(1, 5)
    # host = 'localhost:5006'
    data_list = [{'a': 1, 'b': -5, 'c': 6}, {'a': 2, 'b': 3, 'c': -2},
                 {'a': -1, 'b': 4, 'c': -3}, {'a': 1, 'b': 4, 'c': 4},
                 {'a': 2, 'b': -4, 'c': 2}, {'a': -3, 'b': 12, 'c': -12},
                 {'a': 1, 'b': 0, 'c': 1}, {'a': 2, 'b': 3, 'c': 7},
                 {'a': 4, 'b': 6, 'c': 9}]

    @task
    def send_request(self):
        data = random.choice(self.data_list)
        self.client.post("/equation", json=data)
