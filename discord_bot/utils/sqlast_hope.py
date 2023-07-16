import sqlalchemy.orm

from .server import Server
from .connect_creater import connect


session = connect('discord_bot/assets/secure/database.db')
delay = 10


def create_server(server_id):
    sess = session()
    srv = Server()
    srv.id = server_id
    sess.add(srv)
    sess.commit()
    sess.close()


def server(server_id) -> (Server, sqlalchemy.orm.session.Session):
    sess = session()
    srv = sess.query(Server).get(server_id)
    if not srv:
        create_server(server_id)
        return sess.query(Server).get(server_id)
    return srv, sess
