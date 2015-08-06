import os
from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

bootstrap = Bootstrap( )
mail = Mail( )
lm = LoginManager( )

instance = 'development'

iggybase = Flask( __name__ )

# import configuration
cfg = os.path.join( os.path.dirname( os.path.dirname( os.path.realpath( __file__ ) ) ), 'config', instance + '.py' )
iggybase.config.from_pyfile( cfg )

# initialize extensions
bootstrap.init_app( iggybase )
lm.init_app( iggybase )
mail.init_app( iggybase )

from iggybase.database import init_db
init_db()

from .mod_auth import mod_auth as mod_auth_blueprint
iggybase.register_blueprint( mod_auth_blueprint )

from .mod_core import mod_core as mod_core_blueprint
iggybase.register_blueprint( mod_core_blueprint )

if __name__ == '__main__':
    iggybase.run( )
