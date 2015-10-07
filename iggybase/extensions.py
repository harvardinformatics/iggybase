from flask.ext.mail import Mail
mail = Mail( )

from flask.ext.login import LoginManager
lm = LoginManager( )
lm.session_protection = 'strong'
lm.login_view = 'mod_auth.login'

from flask.ext.bootstrap import Bootstrap
bootstrap = Bootstrap( )