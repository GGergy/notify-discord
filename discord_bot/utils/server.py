import sqlalchemy
import json
from discord_bot.utils.connect_creater import SqlAlchemyBase


class Server(SqlAlchemyBase):
    __tablename__ = 'servers'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    queue = sqlalchemy.Column(sqlalchemy.String, default='{"queue": []}')
    now = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    def get_queue(self):
        return json.loads(self.queue)['queue']

    def pack_queue(self, q):
        self.queue = json.dumps({"queue": q})
