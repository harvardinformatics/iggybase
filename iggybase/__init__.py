from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.login import LoginManager
from importlib import import_module
from iggybase.database import init_db
import config


mail = Mail( )
lm = LoginManager( )
bootstrap = Bootstrap( )

iggybase = Flask( __name__ )

# initialize extensions
bootstrap.init_app( iggybase )
lm.init_app( iggybase )
mail.init_app( iggybase )

instance = init_db()

# configuration
cfg = getattr( config, instance )
iggybase.config.from_object( cfg )

from .mod_auth import mod_auth as mod_auth_blueprint
iggybase.register_blueprint( mod_auth_blueprint )

from .mod_core import mod_core as mod_core_blueprint
iggybase.register_blueprint( mod_core_blueprint )

from .mod_admin import mod_admin as mod_admin_blueprint
iggybase.register_blueprint( mod_admin_blueprint )

if __name__ == '__main__':
    iggybase.run( )
