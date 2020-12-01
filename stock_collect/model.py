from . import App, peewee


class _BaseModel(peewee.Model):
    class Meta:
        database = App.connection


class Token(_BaseModel):
    token_id = peewee.AutoField()
    token = peewee.CharField()


class News(_BaseModel):
    news_id = peewee.AutoField()
    news = peewee.TextField()
