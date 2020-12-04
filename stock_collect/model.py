from . import App, peewee


class _BaseModel(peewee.Model):
    class Meta:
        database = App.connection


class Token(_BaseModel):
    token = peewee.CharField()


class News(_BaseModel):
    time = peewee.DateTimeField()
    news = peewee.TextField()


App.connection.create_tables([Token, News], safe=True)
