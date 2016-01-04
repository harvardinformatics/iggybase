from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import get_config
import logging
conf = get_config( )

adminengine = create_engine( conf.SQLALCHEMY_DATABASE_URI + conf.ADMIN_DB_NAME )
admin_db_session = scoped_session( sessionmaker( autocommit = False, autoflush = False, bind = adminengine ) )
StaticBase = declarative_base()
StaticBase.query = admin_db_session.query_property()

engine = create_engine( conf.SQLALCHEMY_DATABASE_URI + conf.DATA_DB_NAME )
db_session = scoped_session( sessionmaker( autocommit = False, autoflush = False, bind = engine ) )
Base = declarative_base()
Base.query = db_session.query_property()

def init_db(  ):

    for i,(module, blueprint) in enumerate(conf.BLUEPRINTS):
        getattr(__import__('iggybase.'+module, fromlist=['models']),'models')
    Base.metadata.create_all( bind = engine )
    StaticBase.metadata.create_all( bind = adminengine )
