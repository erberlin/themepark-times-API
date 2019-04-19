# -*- coding: utf-8 -*-
"""
This module defines a connexion app object and configures the API
endpoints based the swagger.yml configuration file.

copyright: © 2019 by Erik R Berlin.
license: MIT, see LICENSE for more details.

"""

import connexion

app = connexion.App(__name__, specification_dir="./")
app.app.url_map.strict_slashes = False
app.add_api("swagger.yml")

if __name__ == "__main__":
    # FLASK_ENV=development & FLASK_DEBUG=1 w/ Docker don't seem to enable debug mode.
    app.run(debug=True)
