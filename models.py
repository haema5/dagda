#!/usr/bin/python3
# -*- coding: utf-8 -*-

from peewee import PostgresqlDatabase
from peewee import Model
from peewee import IntegerField, CharField, \
    DateTimeField, IdentityField, ForeignKeyField, \
    TextField

from playhouse.postgres_ext import JSONField
# from playhouse.shortcuts import model_to_dict, dict_to_model, update_model_from_dict

import datetime

from config import *

# Connect to a Postgres database.
pg_db = PostgresqlDatabase(
    PG_DB,
    user=PG_USER,
    password=PG_SEC,
    host=PG_HOST,
    port=PG_PORT
)


class BaseModel(Model):
    """A base model that will use our Postgres database"""

    class Meta:
        database = pg_db


class User(BaseModel):
    """Table user"""
    id = IdentityField()
    login = CharField(unique=True)
    password = CharField(null=False)
    email = CharField(unique=True)
    display_name = CharField(null=True)
    join_date = DateTimeField(default=datetime.datetime.now)
    last_login = DateTimeField(default=datetime.datetime.now)
    status = IntegerField(default=1)
    url = CharField(null=True)


class Meta(BaseModel):
    """Table meta"""
    id = IdentityField()
    key = CharField()
    value = CharField()
    user_id = ForeignKeyField(User, backref='metas')


class Harp(BaseModel):
    """Table harp"""
    id = IdentityField()
    data = JSONField()
    user_id = ForeignKeyField(User, backref='harps')


class Auth(BaseModel):
    """Table auth"""
    token = CharField()
    user_id = ForeignKeyField(User, backref='tokens')


class Debug(BaseModel):
    """Table debug"""
    id = IdentityField()
    date = DateTimeField(default=datetime.datetime.now)
    event = TextField()


# Processing:
def create_tables():
    """Create all tables in DB"""
    with pg_db:
        pg_db.create_tables([User, Meta, Harp, Auth, Debug])


def drop_tables():
    """Drop all tables in DB"""
    with pg_db:
        pg_db.drop_tables([User, Meta, Harp, Auth, Debug])


if __name__ == '__main__':
    drop_tables()
    create_tables()
    print('Ok')
