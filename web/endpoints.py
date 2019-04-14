# -*- coding: utf-8 -*-
"""
This module implements API endpoint handlers to query the database and
return data for the connexion app.

copyright: © 2019 by Erik R Berlin.
license: MIT, see LICENSE for more details.

"""

from flask import abort, json

from data_access import DBClient

unspecified = object()


def read_parks():
    """Handler for /parks endpoint.

    Retrieves schedule data for all parks from database.

    Returns
    -------
    list of dicts

    Raises
    ------
    werkzeug.exceptions.NotFound
        If no park schedules are found.

    """

    with DBClient() as DB:
        parks_data = DB.read_park_schedules()
    response = []
    for _, data in parks_data.items():
        response.append(json.loads(data))
    if response:
        return response
    else:
        abort(404, f"No park schedules found.")


def read_park(park_id):
    """Handler for /parks/{park_id} endpoint.

    Retrieves schedule data for the specified park from database.

    Parameters
    ----------
    park_id : str
        A park ID.

    Returns
    -------
    dict

    Raises
    ------
    werkzeug.exceptions.NotFound
        If no match is found for `park_id`.

    """

    with DBClient() as DB:
        park_data = DB.read_park_schedule(park_id=park_id)
    if park_data:
        return json.loads(park_data)
    else:
        abort(404, f"Park ID not found.")


def read_experiences(park_id, _type=unspecified):
    """Handler for /parks/{park_id}/experiences endpoint.

    Retrieves all experiences under the specified park from database.

    Parameters
    ----------
    park_id : str
        A park ID.
    _type : str, optional
        Experience type used for filtering.

    Returns
    -------
    list of dicts

    Raises
    ------
    werkzeug.exceptions.NotFound
        If no match is found for `park_id`.
        If `_type` is specified but no match is found.

    """

    with DBClient() as DB:
        experience_data = DB.read_experiences(park_id=park_id)
    if not experience_data:
        abort(404, f"Park ID not found.")
    response = []
    for _, data in experience_data.items():
        experience = json.loads(data)
        if _type is unspecified:
            response.append(experience)
        elif _type is not unspecified and _type.lower() == experience["type"].lower():
            response.append(experience)

    if response:
        return response
    elif _type is not unspecified:
        # park_id returned results but no match for _type.
        abort(404, f"Experience of type '{_type}' not found.")


def read_experience(park_id, experience_id):
    """Handler for /parks/{park_id}/experiences/{experience_id} endpoint

    Retrieves one experience from database.

    Parameters
    ----------
    park_id : str
        A park ID.
    experience_id : str
        An experience ID.

    Returns
    -------
    dict

    Raises
    ------
    werkzeug.exceptions.NotFound
        If no match is found for `park_id` and/or `experience_id`.

    """

    with DBClient() as DB:
        experience_data = DB.read_experience(
            park_id=park_id, experience_id=experience_id
        )
    if experience_data:
        return json.loads(experience_data)
    else:
        abort(404, f"Park and/or experience ID not found.")
