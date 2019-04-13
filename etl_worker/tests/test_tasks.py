# -*- coding: utf-8 -*-
"""Tests for the etl_worker.tasks module.

copyright: © 2019 by Erik R Berlin.
license: MIT, see LICENSE for more details.

"""

from unittest import mock

from etl_worker.tasks import (
    _api_request,
    _fetch_access_token,
    _fetch_experience_data,
    _load_experience_data,
    _process_experience_data,
    update_experiences,
)


@mock.patch("requests.get")
@mock.patch("etl_worker.tasks._fetch_access_token")
def test__api_request_calls_requests_get(mock_fetch_access_token, mock_get):
    """Calls `requests.get` with expected values."""

    access_token = "BEARER 0123456789abcdef0123456789abcdef"
    expected_headers = {
        "Accept": "application/json;apiversion=1;charset=UTF-8",
        "Authorization": access_token,
    }
    base_url = "https://api.wdpro.disney.go.com"
    endpoint = "/facility-service/theme-parks/330339/wait-times"
    expected_url = "".join([base_url, endpoint])

    mock_fetch_access_token.return_value = access_token
    mock_get.return_value.status_code = 200

    _api_request(api_endpoint=endpoint)
    mock_get.assert_called_with(expected_url, headers=expected_headers)


@mock.patch("requests.get")
@mock.patch("etl_worker.tasks._fetch_access_token")
def test__api_request_returns_response_json(mock_fetch_access_token, mock_get):
    """Returns response.json()."""

    endpoint = "/facility-service/theme-parks/330339/wait-times"
    sample_data = {"sample": "dict"}
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = sample_data

    response = _api_request(api_endpoint=endpoint)
    assert response == sample_data


@mock.patch("requests.post")
def test__fetch_access_token_calls_requests_post(mock_post):
    """Calls `requests.post` with expected values."""

    expected_params = {
        "grant_type": "assertion",
        "assertion_type": "public",
        "client_id": "WDPRO-MOBILE.MDX.WDW.ANDROID-PROD",
    }
    expected_url = "https://authorization.go.com/token"

    _fetch_access_token()
    mock_post.assert_called_with(expected_url, params=expected_params)


@mock.patch("requests.post")
def test__fetch_access_token_returns_token(mock_post):
    """Returns token from response.json() data."""

    mock_post.return_value.ok = True
    mock_post.return_value.json.return_value = {
        "access_token": "0123456789abcdef0123456789abcdef",
        "expires_in": "900",
        "scope": "AUTHZ_PUBLIC-INSECURE",
        "token_type": "BEARER",
    }

    token = _fetch_access_token()
    assert token == "BEARER 0123456789abcdef0123456789abcdef"


@mock.patch("etl_worker.tasks._api_request")
def test__fetch_experience_data_calls_api_request(mock_api_request_func):
    """Calls `_api_request` with expected values."""

    park_id = "330339"
    expected_endpoint = f"/facility-service/theme-parks/{park_id}/wait-times"

    _fetch_experience_data(park_id=park_id)
    mock_api_request_func.assert_called_with(api_endpoint=expected_endpoint)


@mock.patch("etl_worker.tasks._api_request")
def test__fetch_experience_data_returns_json_entries_key(mock_api_request_func):
    """Returns 'entries' key from response.json() data."""

    sample_data = {"entries": {"A": 1, "B": 2}}
    park_id = "330339"

    mock_api_request_func.return_value = sample_data

    data = _fetch_experience_data(park_id=park_id)
    assert data == sample_data["entries"]


@mock.patch("data_access.db_client.DBClient.write_experience_data")
def test__load_experience_data_calls_DBClient(mock_write_experience_data):
    """Calls `DBClient.write_experience_data` with expected values."""

    park_id = "330339"
    sample_data = {"12345678": {"A": 1, "B": 2}}

    _load_experience_data(park_id=park_id, data=sample_data)
    mock_write_experience_data.assert_called_with(park_id=park_id, data=sample_data)


@mock.patch("etl_worker.tasks._load_experience_data")
@mock.patch("etl_worker.tasks._process_experience_data")
@mock.patch("etl_worker.tasks._fetch_experience_data")
def test_update_experiences_count(mock_fetch_data, mock_process_data, mock_load_data):
    """Calls functions to fetch, process and load data 6 times."""

    update_experiences()
    assert mock_fetch_data.call_count == 6
    assert mock_process_data.call_count == 6
    assert mock_load_data.call_count == 6


def test__process_experience_data():
    """Veryfy correct transformation of returned data."""
    input_data = [
        {
            "links": {
                "self": {"href": "https://api.wdpro.disney.go.com/..."},
                "attractions": {"href": "https://api.wdpro.disney.go.com/..."},
            },
            "id": "12345678;entityType=Attraction",
            "name": "Ride A",
            "type": "Attraction",
            "waitTime": {
                "fastPass": {"available": True},
                "status": "Operating",
                "singleRider": False,
                "postedWaitMinutes": 5,
                "rollUpStatus": "Operating",
                "rollUpWaitTimeMessage": "Short Wait Times",
            },
        }
    ]
    expected_output = {
        "12345678": {
            "id": "12345678",
            "name": "Ride A",
            "type": "Attraction",
            "statusInfo": {
                "fastPass": {"available": True},
                "status": "Operating",
                "singleRider": False,
                "postedWaitMinutes": 5,
                "rollUpStatus": "Operating",
                "rollUpWaitTimeMessage": "Short Wait Times",
            },
        }
    }
    output = _process_experience_data(data=input_data)
    assert output == expected_output
