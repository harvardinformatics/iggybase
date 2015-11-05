from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SelectField, ValidationError
from wtforms.validators import DataRequired, Length, email
from .models import User
from iggybase.mod_admin.models import NewUser

class LoginForm( Form ):
    name = StringField( 'Login name', validators = [ DataRequired( ), Length( 1, 16 ) ] )
    password = PasswordField( 'Password', validators = [ DataRequired( ) ] )
    role = SelectField( 'Role', choices = [ ( '', '' ) ], validators = [ DataRequired( ) ] )
    organization = SelectField( 'Organization', choices = [ ( '', '' ) ], validators = [ DataRequired( ) ] )
    remember_me = BooleanField( 'Remember me' )

class RegisterForm( Form ):
    name = StringField( 'Login name', validators = [ DataRequired( ), Length( 1, 16 ) ] )
    first_name = StringField( 'First Name', validators = [ DataRequired( ) ] )
    last_name = StringField( 'Last Name', validators = [ DataRequired( ) ] )
    password = PasswordField( 'Password', validators = [ DataRequired( ) ] )
    confpassword = PasswordField( 'Confirm Password', validators = [ DataRequired( ) ] )
    email = StringField( 'Email', validators = [ email( ), DataRequired( ) ] )
    organization = StringField( 'Organization', validators = [ DataRequired( ) ] )
    address1 = StringField( 'Address 1', validators = [ DataRequired( ) ] )
    address2 = StringField( 'Address 2' )
    city = StringField( 'City', validators = [ DataRequired( ) ] )
    state = StringField( 'state', validators = [ DataRequired( ) ] )
    zip = StringField( 'Zip Code', validators = [ DataRequired( ) ] )
    phone = StringField( 'Phone', validators = [ DataRequired( ) ] )
    group = StringField( 'Group', validators = [ DataRequired( ) ] )
    pi = StringField( 'PI', validators = [ DataRequired( ) ] )

    def validate_email( self, field ):
        if User.query.filter_by( email = field.data ).first( ):
            raise ValidationError( 'Email already exists' )

    def validate_name( self, field ):
        if User.query.filter_by( name = field.data ).first( ):
            raise ValidationError( 'Login name already in use' )
        if NewUser.query.filter_by( name = field.data ).first( ):
            raise ValidationError( 'Login name already in use' )