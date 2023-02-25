from peewee import PostgresqlDatabase, Model, TextField
from cfg import tempory_db_name


class BaseModel(Model):
    class Meta:
        database = PostgresqlDatabase('instagram',user='instagram',password='asdasd1234',host='localhost',port=5432)


class ResultItemModel(BaseModel):
    url = TextField(primary_key=True)
    word = TextField()
    username = TextField()

    @classmethod
    def add_if_not_exists(cls, **kwargs):
        cls.get_or_create(**kwargs)

    @classmethod
    def is_exists(cls, url):
        return cls.select().where(ResultItemModel.url == url).exists()


class Checked(BaseModel):
    url = TextField(primary_key=True)

    @classmethod
    def is_exists(cls, url):
        return cls.select().where(Checked.url == url).exists()
