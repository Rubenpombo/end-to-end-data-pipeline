"""Unit tests for the Airflow DAG ingestion logic (no Airflow or network needed)."""
import sys
from unittest.mock import MagicMock, patch

import pytest
import requests

# The DAG module imports Airflow at module level; stub it so the ingestion
# functions can be unit-tested without Airflow installed.
for module in (
    'airflow',
    'airflow.providers',
    'airflow.providers.standard',
    'airflow.providers.standard.operators',
    'airflow.providers.standard.operators.python',
):
    sys.modules.setdefault(module, MagicMock())

from dags.kafka_stream import format_data, get_data  # noqa: E402

pytestmark = pytest.mark.unit


def sample_api_user():
    """Minimal RandomUser API payload covering every field used by format_data."""
    return {
        'login': {
            'uuid': 'f47ac10b-58cc-4372-a567-0e02b2c3d479',
            'username': 'johndoe',
            'sha256': 'deadbeef',
        },
        'name': {'first': 'John', 'last': 'Doe'},
        'gender': 'male',
        'location': {
            'street': {'number': 42, 'name': 'Main St'},
            'city': 'Springfield',
            'state': 'Illinois',
            'country': 'United States',
            'postcode': 62701,
            'coordinates': {'latitude': '39.7817', 'longitude': '-89.6501'},
            'timezone': {'offset': '-6:00', 'description': 'Central Time (US & Canada)'},
        },
        'email': 'john.doe@example.com',
        'dob': {'date': '1990-05-15T10:20:30.000Z'},
        'registered': {'date': '2015-03-10T08:00:00.000Z'},
        'phone': '555-1234',
        'picture': {'large': 'https://randomuser.me/api/portraits/men/1.jpg'},
        'nat': 'US',
    }


def mock_response(payload, status_code=200):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    if status_code >= 400:
        response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    else:
        response.raise_for_status.return_value = None
    return response


class TestGetData:
    def test_returns_first_result_on_success(self):
        user = sample_api_user()
        with patch('requests.get', return_value=mock_response({'results': [user]})):
            assert get_data() == user

    def test_returns_none_when_results_empty(self):
        with patch('requests.get', return_value=mock_response({'results': []})):
            assert get_data() is None

    def test_returns_none_on_http_error(self):
        with patch('requests.get', return_value=mock_response({}, status_code=500)):
            assert get_data() is None

    def test_returns_none_on_connection_error(self):
        with patch('requests.get',
                   side_effect=requests.exceptions.ConnectionError()):
            assert get_data() is None


class TestFormatData:
    def test_maps_all_top_level_fields(self):
        data = format_data(sample_api_user())

        assert data['id'] == 'f47ac10b-58cc-4372-a567-0e02b2c3d479'
        assert data['first_name'] == 'John'
        assert data['last_name'] == 'Doe'
        assert data['gender'] == 'male'
        assert data['email'] == 'john.doe@example.com'
        assert data['username'] == 'johndoe'
        assert data['password'] == 'deadbeef'
        assert data['phone'] == '555-1234'
        assert data['picture'] == 'https://randomuser.me/api/portraits/men/1.jpg'
        assert data['nationality'] == 'US'

    def test_dates_are_truncated_to_day(self):
        data = format_data(sample_api_user())
        assert data['dob'] == '1990-05-15'
        assert data['registered_date'] == '2015-03-10'

    def test_address_is_nested_and_postcode_stringified(self):
        address = format_data(sample_api_user())['address']

        assert address == {
            'street': '42 Main St',
            'city': 'Springfield',
            'state': 'Illinois',
            'country': 'United States',
            'postcode': '62701',
            'coordinates': {'latitude': '39.7817', 'longitude': '-89.6501'},
            'timezone': {'offset': '-6:00',
                         'description': 'Central Time (US & Canada)'},
        }
