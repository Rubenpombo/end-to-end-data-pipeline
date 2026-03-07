import unittest
import requests

class TestObservabilityHealth(unittest.TestCase):
    SERVICES = {
        "Kafka UI": "http://localhost:8000",
        "Prometheus": "http://localhost:9090",
        "Grafana": "http://localhost:3000"
    }

    def test_services_are_reachable(self):
        """
        Test that observability services are reachable and return success codes.
        """
        for name, url in self.SERVICES.items():
            try:
                response = requests.get(url, timeout=5)
                self.assertIn(response.status_code, [200, 302], f"{name} at {url} is not reachable (Status: {response.status_code})")
                print(f"OK: {name} is up.")
            except requests.exceptions.RequestException as e:
                self.fail(f"{name} at {url} is not reachable: {e}")

if __name__ == "__main__":
    unittest.main()
