# -*- coding: utf-8 -*-
"""Tests for the etl_worker.tasks module.

copyright: © 2019 by Erik R Berlin.
license: MIT, see LICENSE for more details.

"""

from unittest import mock

from etl_worker.tasks import _fetch_access_token


@mock.patch("requests.post")
def test__fetch_access_token(mock_post):
    mock_post.return_value.ok = True
    mock_post.return_value.json.return_value = {
        "access_token": "0123456789abcdef0123456789abcdef",
        "expires_in": "900",
        "scope": "AUTHZ_PUBLIC-INSECURE",
        "token_type": "BEARER",
    }
    token = _fetch_access_token()
    assert token == "BEARER 0123456789abcdef0123456789abcdef"
