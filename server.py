#!/usr/bin/python3
# -*- coding: utf-8 -*-

# import models
from models import User, Meta, Harp, Auth, Debug
from models import create_tables, drop_tables, pg_db

from bottle import Bottle, route, run, error, hook
from bottle import redirect, request, response

from hashlib import sha512

from playhouse.shortcuts import model_to_dict, dict_to_model
import json

# drop_tables()
# create_tables()
app = Bottle()


def _debug(data):
    res = Debug.create(event=data)


def date_to_str(data):
    import datetime
    if isinstance(data, (datetime.date, datetime.datetime)):
        return data.isoformat()


@hook('before_request')
def _connect_db():
    pg_db.connect()


@hook('after_request')
def _close_db():
    if not pg_db.is_closed():
        pg_db.close()
    # return response


@route('/debug', method='GET')
@route('/debug', method='PUT')
@route('/debug', method='POST')
def debug():
    headers_string = ['{}: {}'.format(h, request.headers.get(h)) for h in request.headers.keys()]
    json_data = request.json
    data = 'URL={}, method={}\nheaders:\n{}, \njson: {}'.format(request.url,
                                                                request.method,
                                                                '\n'.join(headers_string),
                                                                json.dumps(json_data)
                                                                )
    _debug(data)
    return data


@route('/json')
def return_json():
    rv = {"id": 1, "name": "Test Item 1"}
    response.content_type = 'application/json'
    return json.dumps(rv)


@route('/', method='GET')
def index():
    data = {'message': 'Hello, World!'}
    response.content_type = 'application/json'
    return json.dumps(data)


@route('/users', methos='GET')
def list_users():
    user_obj = User.select(User.login, User.join_date).get()
    user_obj = model_to_dict(user_obj)

    json_data = json.dumps(user_obj,
                           sort_keys=True,
                           indent=1,
                           default=date_to_str)

    return json_data


@route('/sign-up', method='POST')
def sign_up():
    data = request.json
    if (data is None) or (data == {}):
        answer = 'Request is empty'
        return answer

    if User.select().where(User.login == data['login']):
        answer = f'Login already exists'
        return answer

    if User.select().where(User.email == data['email']):
        answer = f'Email already exists'
        return answer

    data['password'] = sha512(data['password'].encode()).hexdigest()
    user = User.create(**data)
    answer = str(user.id)

    return answer


@route('/restore', method='GET')
def restore():
    data = request.json
    if (data is None) or (data == {}):
        answer = 'Request is empty'
        return answer

    if not User\
            .select()\
            .where(User.login == data['login']):
        answer = f"Can't find user"
        return answer

    if not User\
            .select()\
            .where((User.login == data['login']) &
                   (User.email == data['email'])):
        answer = f"Email does not match user"
        return answer

    def generate_passwd():
        from random import choices
        from string import ascii_letters, digits

        random_passwd = ''.join(choices(ascii_letters + digits, k=8))
        return random_passwd

    new_passwd = generate_passwd()
    hash_passwd = sha512(new_passwd.encode()).hexdigest()

    user = (User
            .update({User.password: hash_passwd})
            .where(User.login == data['login'])
            .execute())

    return new_passwd


if __name__ == "__main__":
    run(host='127.0.0.1', port=8000, reloader=True, quiet=False, debug=True)
