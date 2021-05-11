# Backend API boilerplate

[![Build Status](https://travis-ci.com/excalibur1987/flask-api-backend-boilerplate.svg?branch=master)](https://travis-ci.com/excalibur1987/flask-api-backend-boilerplate)

This is the backend api boilerplate to be used with other frontend apps.

## This boilerplate is built using the following dependencies

- Flask
- Sqlalchemy
- Flask-Restful
- Flask-JWT-Extended
- Flask-Principal

## Usage

To start intial setup run `source intialize.sh` then make sure to have the following environment variable `DATABASE_URL` & `SECRET_KEY`.

This backend uses flask-restful class based resources. A helper function available is "has_roles", it's used as following.

    from flask_restful import Resource
    from app.utils import has_roles

    class MyResource(Resource):

        # has_roles checks for availability of all provided roles.
        # you can provide a list as argument and it will return True if one of it's roles is present
        @has_roles('staff', ['manager', 'admin'])
        def get(self):
            data = "This is a response"
            return data
