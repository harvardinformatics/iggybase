from sqlalchemy import create_engine, exc, event
from sqlalchemy.pool import Pool
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import get_config
from threading import Lock
import logging

conf = get_config()


# used to create an object that mimics the object created by SQLAlchemy(app)
# used for flask-security
class DB_Factory:
    def __init__(self, query, session):
        self.session = session
        self.Query = query
        self._engine_lock = Lock()
        self.use_native_unicode = True
        self.Model = None
        self.app = None


engine = create_engine(conf.SQLALCHEMY_DATABASE_URI + conf.DATA_DB_NAME)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
db = DB_Factory(Base.query, db_session)


def init_db():
    from iggybase.mod_admin import models
    getattr(__import__('iggybase', fromlist=['models']), 'models')
    Base.metadata.create_all(bind=engine)


@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
        raise exc.DisconnectionError()

    cursor.close()