from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class DefaultForm( Form ):
    hello = StringField( 'hello', validators=None, filters=(), description=u'', id=None, default='Hello' )
