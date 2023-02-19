from peewee import SqliteDatabase, Model, TextField
from cfg import tempory_db_name


class ResultItemModel(Model):
    class Meta:
        database = SqliteDatabase(tempory_db_name)

    url = TextField(primary_key=True)
    word = TextField()

    @classmethod
    def add_if_not_exists(cls, **kwargs):
        cls.get_or_create(**kwargs)

    @classmethod
    def is_exists(cls, url):
        return cls.select().where(ResultItemModel.url == url).exists()


class Checked(Model):
    class Meta:
        database = SqliteDatabase(tempory_db_name)

    url = TextField(primary_key=True)

    @classmethod
    def is_exists(cls, url):
        return cls.select().where(Checked.url == url).exists()
