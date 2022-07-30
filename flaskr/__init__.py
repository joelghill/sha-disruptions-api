import os
import json

from flask import Flask, request, jsonify
from flasgger import Swagger, LazyString, LazyJSONEncoder
from importlib_metadata import distribution
from flaskr.scrape import get_all_disruptions, BASE_URL, DISRUPTIONS_URL


URL = f"{BASE_URL}/{DISRUPTIONS_URL}"


def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY="dev",
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize Swagger
    app.json_encoder = LazyJSONEncoder
    template = dict(
        info={
            "title": "SHA Service Disruptions",
            "description": "Unofficial API used to retrieve information about communities with health service disruptions in Saskatchewan",
            "contact": {
                "responsibleDeveloper": "Joel Hill",
                "email": "joelghill@protonmail.me",
                "url": "https://github.com/joelghill",
            },
            "version": "1.0.0",
        },
        host=LazyString(lambda: request.host),
        schemes=[LazyString(lambda: "https" if request.is_secure else "http")],
        basePath="",  # base bash for blueprint registration
    )

    # Initialize swagger documentation
    Swagger(app, template=template)

    @app.route("/v1/disruptions")
    def service_disruptions():
        """
        file: ../openapi/disruptions.yml
        """
        disruptions = get_all_disruptions(URL)

        return jsonify(disruptions)

    return app


