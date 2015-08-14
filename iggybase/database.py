from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from iggybase import iggybase as Iggy

staticengine = create_engine( Iggy.config[ 'SQLALCHEMY_DATABASE_URI' ] + Iggy.config[ 'STATIC_DB_NAME' ] )
static_db_session = scoped_session( sessionmaker( autocommit = False, autoflush = False, bind = staticengine ) )
StaticBase = declarative_base()
StaticBase.query = static_db_session.query_property()

import iggybase.mod_static.models
StaticBase.metadata.create_all( bind = staticengine )

from .mod_static.models import Lab, Iggybase_Instance

session = static_db_session( )
lab = session.query( Lab ).filter( Lab.lab_name == Iggy.config[ 'LAB' ] ).first( )
iggybaseinstance = session.query( Iggybase_Instance ).filter( Iggybase_Instance.lab_id == lab.lab_id ).filter( Iggybase_Instance.instance_name == Iggy.config[ 'INSTANCE_NAME' ] ).first( )

engine = create_engine( Iggy.config[ 'SQLALCHEMY_DATABASE_URI' ] + iggybaseinstance.database )
db_session = scoped_session( sessionmaker( autocommit = False, autoflush = False, bind = engine ) )
Base = declarative_base()
Base.query = db_session.query_property()

def init_db( ):
    import iggybase.mod_auth.models
    import iggybase.mod_core.models
    Base.metadata.create_all( bind = engine )

