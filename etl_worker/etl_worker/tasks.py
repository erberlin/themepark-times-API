# -*- coding: utf-8 -*-
"""
etl_worker.tasks
----------------
This module implements tasks to retrieve data for U.S. parks from
https://api.wdpro.disney.go.com, tranform it, and load it into Redis.

copyright: © 2019 by Erik R Berlin.
license: MIT, see LICENSE for more details.

"""

import requests
import requests_cache


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
