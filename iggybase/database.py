from flask import session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import Config
import os, socket

rootdir = os.path.basename( Config._basedir )
hostname = socket.gethostname()

adminengine = create_engine( Config.SQLALCHEMY_DATABASE_URI + Config.ADMIN_DB_NAME )
admin_db_session = scoped_session( sessionmaker( autocommit = False, autoflush = False, bind = adminengine ) )
StaticBase = declarative_base()
StaticBase.query = admin_db_session.query_property()

import iggybase.mod_admin.models
StaticBase.metadata.create_all( bind = adminengine )

from iggybase.mod_admin.models import Iggybase_Instance

ad_session = admin_db_session( )
iggybaseinstance = ad_session.query( Iggybase_Instance ).filter( Iggybase_Instance.host_name == hostname ).filter( Iggybase_Instance.root_dir == rootdir ).first( )

instance = iggybaseinstance.instance_name

engine = create_engine( Config.SQLALCHEMY_DATABASE_URI + iggybaseinstance.database )
db_session = scoped_session( sessionmaker( autocommit = False, autoflush = False, bind = engine ) )
Base = declarative_base()
Base.query = db_session.query_property()

def init_db( ):
    import iggybase.mod_auth.models
    import iggybase.mod_core.models
    Base.metadata.create_all( bind = engine )

    return instance

