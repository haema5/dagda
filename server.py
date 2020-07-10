#!/usr/bin/python3
# -*- coding: utf-8 -*-

# import models
from models import User, Meta, Harp, Auth, create_tables, drop_tables, pg_db

from bottle import Bottle, route, run, error, hook
from bottle import redirect, request, response

from hashlib import sha512

import json

# drop_tables()
create_tables()
app = Bottle()


@hook('before_request')
def _connect_db():
    pg_db.connect()


@hook('after_request')
def _close_db():
    if not pg_db.is_closed():
        pg_db.close()
    # return response


@route('/json')
def return_json():
    rv = {"id": 1, "name": "Test Item 1"}
    response.content_type = 'application/json'
    return json.dumps(rv)


@route('/', method='GET')
def index():
    return 'Quake II - forever!'


# @route('/users/<user_id>', methos='GET')
# def list_users(user_id):
#     output = recources.show_users(user_id)
#     return output


@route('/sign-up', method='POST')
def sign_up():
    data = request.json
    if (data is None) or (data == {}):
        answer = 'Request is empty'
        return answer

    if User.select().where(User.login == data['login']):
        answer = f'Login {data["login"]} already exists'
        return answer

    if User.select().where(User.email == data['email']):
        answer = f'Email {data["email"]} already exists'
        return answer

    data['password'] = sha512(data['password'].encode()).hexdigest()

    # user, status = User.get_or_create(**data)
    # answer = {'id': str(user), 'status': str(status)}

    user = User.create(**data)
    answer = str(user.id)
    return answer


@route('/restore', method='GET')
def restore():
    data = request.json
    if (data is None) or (data == {}):
        answer = 'Request is empty'
        return answer

    if not User.select().where(User.login == data['login']):
        answer = f"Can't find {data['login']}"
        return answer

    if not User.select().where(User.email == data['email']):
        answer = f"Email does not match user {data['login']}"
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
