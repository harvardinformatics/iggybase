from flask.ext.wtf import Form
from wtforms import StringField, IntegerField, BooleanField, DateField, TextAreaField, FloatField, SelectField,\
    FileField, PasswordField, DecimalField
from wtforms.validators import DataRequired, Length, email, Optional

class CacheForm(Form):
    key = StringField('Key')
    value = StringField('Value')
    refresh_obj = StringField('Refresh Object')
    version = StringField('Version')
