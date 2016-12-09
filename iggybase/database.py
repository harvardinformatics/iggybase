from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from config import Config
from threading import Lock
from datetime import datetime
import re
import logging

conf = Config()


class IggybaseBase(object):
    def __init__(self, *args, **kwargs):
        if 'extendable' in kwargs:
            self.extendable = kwargs['extendable']
        else:
            self.extendable = None

        if 'extended_table' in kwargs:
            self.extended_table = kwargs['extended_table']
        else:
            self.extended_table = None

    @declared_attr
    def __tablename__(cls):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def __iter__(self):
        values = vars(self)
        for attr in self.__table__.columns.keys():
            if attr in values:
                yield attr, values[attr]
            else:
                yield attr, None

    def values(self):
        return dict(self)

    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean)

    @declared_attr
    def organization_id(cls):
        return Column('organization_id', ForeignKey('organization.id'))

    @declared_attr
    def organization_fk(cls):
        return relationship("Organization", primaryjoin="Organization.id==%s.organization_id" % cls.__name__)

    order = Column(Integer)


# used to create an object that mimics the object created by SQLAlchemy(app)
# used for flask-security
class DBFactory:
    def __init__(self, query, session):
        self.session = session
        self.Query = query
        self._engine_lock = Lock()
        self.use_native_unicode = True
        self.Model = None
        self.app = None


engine = create_engine(conf.SQLALCHEMY_DATABASE_URI + conf.DATA_DB_NAME, pool_recycle=3600)
db_sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(db_sessionmaker)
Base = declarative_base(cls=IggybaseBase)
Base.query = db_session.query_property()
db = DBFactory(Base.query, db_session)


def init_db():
    getattr(__import__('iggybase', fromlist=['models']), 'models')
    Base.metadata.create_all(bind=engine)
