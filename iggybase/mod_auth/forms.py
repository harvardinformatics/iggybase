from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import Input

class LoginForm( Form ):
    username = StringField( 'Username', validators = [ DataRequired( ), Length( 1, 16 ) ] )
    password = PasswordField( 'Password', validators = [ DataRequired( ) ] )
    remember_me = BooleanField( 'Remember me' )
    login = SubmitField( 'Login' )
