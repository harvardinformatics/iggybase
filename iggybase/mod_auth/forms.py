from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import Input, HTMLString, html_params


#class ButtonInput( Input ):
#    input_type = 'button'
#
#    def __call__(self, field, **kwargs):
#        kwargs.setdefault('value', field.label.text)
#        return super(ButtonInput, self).__call__(field, **kwargs)


class ButtonInput( object ):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        val = field.label.text
        field.label = None
        return HTMLString('<input %s>' % html_params(name=field.name, type='button', value=val, **kwargs))


class ButtonField( BooleanField ):
    widget = ButtonInput()


class LoginForm( Form ):
    username = StringField( 'Username', validators = [ DataRequired( ), Length( 1, 16 ) ] )
    password = PasswordField( 'Password', validators = [ DataRequired( ) ] )
    remember_me = BooleanField( 'Remember me' )
    login = SubmitField( 'Login' )
    register = ButtonField( 'Register' )

class RegisterForm( Form ):
    username = StringField( 'Username', validators = [ DataRequired( ), Length( 1, 16 ) ] )
    first = StringField( 'First Name', validators = [ DataRequired( ) ] )
    last = StringField( 'Last Name', validators = [ DataRequired( ) ] )
    password = PasswordField( 'Password', validators = [ DataRequired( ) ] )
    confpassword = PasswordField( 'Confirm Password', validators = [ DataRequired( ) ] )
    email = StringField( 'Email', validators = [ DataRequired( ) ] )
    institution = StringField( 'Institution', validators = [ DataRequired( ) ] )
    address1 = StringField( 'Address 1', validators = [ DataRequired( ) ] )
    address2 = StringField( 'Address 2', validators = [ DataRequired( ) ] )
    city = StringField( 'City', validators = [ DataRequired( ) ] )
    state = StringField( 'state', validators = [ DataRequired( ) ] )
    zip = StringField( 'Zip Code', validators = [ DataRequired( ) ] )
    phone = StringField( 'Phone', validators = [ DataRequired( ) ] )
    group = StringField( 'Group', validators = [ DataRequired( ) ] )
    pi = StringField( 'PI', validators = [ DataRequired( ) ] )
    register = SubmitField( 'Register' )