from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from iggybase import iggybase as Iggy

adminengine = create_engine( Iggy.config[ 'SQLALCHEMY_DATABASE_URI' ] + Iggy.config[ 'ADMIN_DB_NAME' ] )
admin_db_session = scoped_session( sessionmaker( autocommit = False, autoflush = False, bind = adminengine ) )
StaticBase = declarative_base()
StaticBase.query = admin_db_session.query_property()

import iggybase.mod_admin.models
StaticBase.metadata.create_all( bind = adminengine )

from .mod_admin.models import Lab, Iggybase_Instance

session = admin_db_session( )
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

