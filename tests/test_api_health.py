import unittest
import requests

class TestAPIHealth(unittest.TestCase):
    API_URL = "https://randomuser.me/api/"

    def test_api_is_reachable(self):
        """
        Test that the API is reachable and returns a successful HTTP status code.
        """
        try:
            response = requests.get(self.API_URL, timeout=10)
            response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx
            self.assertEqual(response.status_code, 200, "API is not reachable or returned an error.")
        except requests.exceptions.RequestException as e:
            self.fail(f"API is not reachable: {e}")

    def test_api_returns_valid_data(self):
        """
        Test that the API returns valid data with a non-empty 'results' field.
        """
        try:
            response = requests.get(self.API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Check if 'results' exists and is not empty
            self.assertIn('results', data, "API response does not contain 'results'.")
            self.assertGreater(len(data['results']), 0, "API 'results' field is empty.")
        except requests.exceptions.RequestException as e:
            self.fail(f"API is not reachable: {e}")

if __name__ == "__main__":
    unittest.main()