import os
from datetime import datetime, timedelta, timezone

from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flask_caching import Cache
from flaskr.scrape import get_all_disruptions, BASE_URL, DISRUPTIONS_URL
from flaskr import config


URL = f"{BASE_URL}/{DISRUPTIONS_URL}"


def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY="dev",
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_object(config)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize Swagger
    app.json_encoder = LazyJSONEncoder
    template = {
        "info": {
            "title": "SHA Service Disruptions",
            "description": "Unofficial API used to retrieve information about communities with health service disruptions in Saskatchewan",
            "contact": {
                "responsibleDeveloper": "Joel Hill",
                "email": "joelghill@protonmail.me",
                "url": "https://github.com/joelghill",
            },
            "version": "1.0.0",
        },
        "host": LazyString(lambda: request.host),
        "schemes": [LazyString(lambda: "https" if request.is_secure else "http")],
        "basePath": "",  # base bash for blueprint registration
    }

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "v1",
                "route": "/v1.json",
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        # "static_folder": "static",  # must be set by user
        "swagger_ui": True,
        "specs_route": "/v1/",
        "swagger": "2.0"
    }

    # Initialize Cache
    cache = Cache(app)

    # Initialize swagger documentation
    Swagger(app, template=template, config=swagger_config)

    # Create Endpoint
    @app.route("/v1/disruptions")
    def service_disruptions():
        """
        file: ../openapi/disruptions.yml
        """
        now = datetime.now(tz=timezone.utc)
        # get the last cache
        last_accessed = cache.get("last_cache")

        # If there was a cached date
        if last_accessed:
            # compare to current time
            difference: timedelta = now - last_accessed

            # If it's been more than a day...
            if difference.days >= 1:
                # get the disruptions
                disruptions = get_all_disruptions(URL)
                # cache current time and disruptions
                cache.set("last_cache", now)
                cache.set("disruptions", disruptions)
            else:
                # Get from cache
                disruptions = cache.get("disruptions")
        else:
            # No cached data
            disruptions = get_all_disruptions(URL)
            # cache current time and disruptions
            cache.set("last_cache", now)
            cache.set("disruptions", disruptions)

        return jsonify(disruptions)

    return app
