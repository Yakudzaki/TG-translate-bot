from peewee import *


db = SqliteDatabase(
    './database.db'
)


class User(Model):
    user_id = IntegerField(
        unique=True,
        null=False
    )
    translate_count = IntegerField(
        null=False,
        default=0
    )

    class Meta:
        db_column = 'users'
        database = db

class Translate(Model):
    translate_id = AutoField()
    text = TextField(
        null=False
    )

    class Meta:
        db_column = 'translates'
        database = db


def create_tables() -> None:
    User.create_table()
    Translate.create_table()


def create_user(user_id: int) -> User:
    return User.create(
        user_id=user_id
    )

def get_user(user_id: int) -> User | None:
    return User.get_or_none(
        user_id=user_id
    )

def add_count_translate(user_id: int):
    user = get_user(user_id)

    user.translate_count += 1
    user.save()

def add_translate(text: str) -> Translate:
    return Translate.create(
        text=text
    )

def get_translate_text(translate_id: int):
    return Translate.get(
        translate_id=translate_id
    ).text