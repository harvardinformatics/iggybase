from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from iggybase import iggybase

engine = create_engine( iggybase.config[ 'SQLALCHEMY_DATABASE_URI' ] )
db_session = scoped_session( sessionmaker( autocommit = False, autoflush = False, bind = engine ) )
Base = declarative_base()
Base.query = db_session.query_property()

staticengine = create_engine( iggybase.config[ 'SQLALCHEMY_DATABASE_URI_STATIC' ] )
static_db_session = scoped_session( sessionmaker( autocommit = False, autoflush = False, bind = staticengine ) )
StaticBase = declarative_base()
StaticBase.query = db_session.query_property()

def init_db():
    import iggybase.mod_static.models
    StaticBase.metadata.create_all( bind = staticengine )

    import iggybase.mod_auth.models
    import iggybase.mod_core.models
    Base.metadata.create_all( bind = engine )

