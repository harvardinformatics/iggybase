from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from iggybase.iggybase import config
import os
import socket

rootdir = os.path.basename( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )
hostname = socket.gethostname()
config_name = hostname + '.' + rootdir

adminengine = create_engine( config[ config_name ].SQLALCHEMY_DATABASE_URI + config[ config_name ].ADMIN_DB_NAME )
admin_db_session = scoped_session( sessionmaker( autocommit = False, autoflush = False, bind = adminengine ) )
StaticBase = declarative_base()
StaticBase.query = admin_db_session.query_property()

engine = create_engine( config[ config_name ].SQLALCHEMY_DATABASE_URI + config[ config_name ].DATA_DB_NAME )
db_session = scoped_session( sessionmaker( autocommit = False, autoflush = False, bind = engine ) )
Base = declarative_base()
Base.query = db_session.query_property()

def init_db( ):
    import iggybase.mod_admin.models
    StaticBase.metadata.create_all( bind = adminengine )

    import iggybase.mod_auth.models
    import iggybase.mod_core.models
    Base.metadata.create_all( bind = engine )

