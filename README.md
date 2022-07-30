# Saskatchewan Health Authority Service Disruptions API
Backend API to serve SHA service disruptions in an easy to consume API.

Service disruptions sourced from the [SK Health Authority Website](https://www.saskhealthauthority.ca/news-events/service-disruptions)

## Dependencies

* [Pipenv](https://pipenv.pypa.io/en/latest/): Python Dev Workflow for Humans
* [Flasgger](https://github.com/flasgger/flasgger): A Flask extension to extract OpenAPI-Specification from all Flask views registered in your API.

## Quick Start
```
pipenv install
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
``` 

Go to http://localhost:5000/apidocs for API documentation