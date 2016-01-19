from sqlalchemy import create_engine
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
    for i, (module, blueprint) in enumerate(conf.BLUEPRINTS):
        getattr(__import__('iggybase.' + module, fromlist=['models']), 'models')
    Base.metadata.create_all(bind=engine)
