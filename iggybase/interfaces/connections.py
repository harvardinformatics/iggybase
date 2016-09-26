from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import Config
import logging

conf = Config()

SpinalBase = declarative_base()
spinal_db_session = None
try:
    spinal_engine = create_engine(conf.SPINAL_DATABASE_URI + conf.SPINAL_DB_NAME, pool_recycle=3600)
    spinal_db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=spinal_engine))
    SpinalBase.query = spinal_db_session.query_property()

    SpinalBase.metadata.create_all(bind=spinal_engine)
except:
    print('Spinal DB might be down')
    logging.error('Could not connect to spinal DB') 
