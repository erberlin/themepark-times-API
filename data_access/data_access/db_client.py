# -*- coding: utf-8 -*-
"""
data_access.db_client
----------------
This module implements `DBClient` used by the themepark-times-API
project to interact with Redis.

copyright: © 2019 by Erik R Berlin.
license: MIT, see LICENSE for more details.

"""

import json
import redis


class DBClient:
    """DB client to interact with Redis."""

    def __init__(self):
        self.r = redis.Redis(
            host="127.0.0.1",
            port="6379",
            password="Aredispassword",
            charset="utf-8",
            decode_responses=True,
        )

    def __enter__(self,):
        return self

    def __exit__(self, *args):
        self.r.connection_pool.disconnect()

    def read_experience(self, *, park_id, experience_id):
        """Read one experience from DB.

        Parameters
        ----------
        park_id : str
            ID of park.
        experience_id : str
            ID of experience.

        Returns
        -------
        dict

        """

        db_key = f"{park_id}:experiences"
        return json.loads(self.r.hget(db_key, experience_id))

    def read_experiences(self, *, park_id):
        """Read all experiences in a park from DB.

        Parameters
        ----------
        park_id : str
            ID of park.

        Returns
        -------
        dict of dicts

        """

        db_key = f"{park_id}:experiences"
        return self.r.hgetall(db_key)

    def read_park_schedule(self, park_id):
        """Read a park schedule from DB.

        Parameters
        ----------
        park_id : str
            ID of park.

        Returns
        -------
        dict

        """

        return json.loads(self.r.hget("parks", park_id))

    def read_park_schedules(self):
        """Read all park schedules from DB.

        Returns
        -------
        dict of dicts

        """

        return self.r.hgetall("parks")

    def write_experience_data(self, *, park_id, data):
        """Write updated experience data to DB.

        Deletes the existing hash first and then writes the new data.
        All operations are executed atomically through a pipeline with
        transaction enabled, so that reads won't occur inbetween.

        Parameters
        ----------
        park_id : str
            ID of park.
        data : dict
            Holds dicts of experience data.

        """

        db_key = f"{park_id}:experiences"
        pipe = self.r.pipeline(transaction=True)
        pipe.delete(db_key)
        for experience_id, experience_data in data.items():
            pipe.hset(
                db_key, experience_id, json.dumps(experience_data, sort_keys=True)
            )
        pipe.execute()

    def write_park_schedule(self, *, park_id, data):
        """Write updated park schedule to DB.

        Parameters
        ----------
        park_id : str
            ID of park.
        data : dict
            Schedule data.

        """

        self.r.hset("parks", park_id, json.dumps(data, sort_keys=True))
