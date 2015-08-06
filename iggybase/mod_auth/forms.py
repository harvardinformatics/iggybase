from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm( Form ):
    username = StringField( 'Username', validators = [ DataRequired( ), Length( 1, 16 ) ] )
    password = PasswordField( 'Password', validators = [ DataRequired( ) ] )
    remember_me = BooleanField( 'Remember me' )
    submit = SubmitField( 'Login' )
    register = SubmitField( 'Register' )