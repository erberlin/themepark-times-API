# -*- coding: utf-8 -*-
"""
etl_worker.tasks
----------------
This module implements tasks to retrieve data for U.S. parks from
https://api.wdpro.disney.go.com, tranform it, and load it into Redis.

copyright: © 2019 by Erik R Berlin.
license: MIT, see LICENSE for more details.

"""

from time import sleep

import requests
import requests_cache

parks = {
    "80007944": {"name": "Magic Kingdom Park", "slug": "magic-kingdom"},
    "80007838": {"name": "Epcot", "slug": "epcot"},
    "80007998": {"name": "Disney's Hollywood Studios", "slug": "hollywood-studios"},
    "80007823": {
        "name": "Disney's Animal Kingdom Theme Park",
        "slug": "animal-kingdom",
    },
    "330339": {"name": "Disneyland Park", "slug": "disneyland"},
    "336894": {
        "name": "Disney California Adventure Park",
        "slug": "disney-california-adventure",
    },
}


def _api_request(*, api_endpoint):
    """Add http headers and makes GET request to specified API endpoint.

    Parameters
    ----------
    api_endpoint : str
        A string representing the target API endpoint for the request.

    Returns
    -------
    dict
        Decoded JSON from API response.

    """

    base_url = "https://api.wdpro.disney.go.com"
    request_url = "".join([base_url, api_endpoint])
    headers = {"Accept": "application/json;apiversion=1;charset=UTF-8"}
    # TODO: Replace ugly retry loop.
    for i in range(1, 6):  # Make 5 attemts to get a valid response.
        headers["Authorization"] = _fetch_access_token()
        r = requests.get(request_url, headers=headers)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 401:  # Unauthorized
            requests_cache.core.clear()
        else:
            sleep((i ** 4) / 100)  # Sleeps for 0.01, 0.16, 0.81, 2.56 and 6.25 seconds.


def _fetch_access_token():
    """Make http POST request to obtain new API access token.

    The access token is valid for 15 minutes, and the response is cached
    for 14 minutes so that the token can be reused.

    Returns
    -------
    str
        Access token for https://api.wdpro.disney.go.com API.

    """
    params = {
        "grant_type": "assertion",
        "assertion_type": "public",
        "client_id": "WDPRO-MOBILE.MDX.WDW.ANDROID-PROD",
    }
    with requests_cache.enabled(
        "token_cache", backend="memory", allowable_methods=("POST",), expire_after=840
    ):
        r = requests.post("https://authorization.go.com/token", params=params)
    if r.ok:
        auth_data = r.json()
        return f"{auth_data['token_type']} {auth_data['access_token']}"
    else:
        return None


def _fetch_experience_data(*, park_id):
    """Uses `_api_request` to call the '/{park_id}/wait-times' enpoint.

    Parameters
    ----------
    park_id : str
        ID number of a park.

    Returns
    -------
    list of dicts
        Attraction & entertainment records from API response.

    """

    api_endpoint = f"/facility-service/theme-parks/{park_id}/wait-times"
    api_response = _api_request(api_endpoint=api_endpoint)
    if api_response:
        return api_response["entries"]


def _process_experience_data(*, data):
    """Extracts status data from API response.

    Parameters
    ----------
    data : list of dicts
        Attraction & entertainment records from API.

    Returns
    -------
    dict

    """

    experiences = {}
    for entry in data:
        new_record = {}
        new_record["id"] = entry["id"].split(";")[0]
        new_record["name"] = entry["name"]
        new_record["type"] = entry["type"]
        new_record["statusInfo"] = entry["waitTime"]
        experiences[new_record["id"]] = new_record
    return experiences


def update_experiences():
    """Pull new experience data and update database for all parks."""

    for park_id in parks.keys():
        data = _fetch_experience_data(park_id=park_id)
        if data:
            _process_experience_data(data=data)
