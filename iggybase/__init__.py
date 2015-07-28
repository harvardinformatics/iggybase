from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, DateField, TextAreaField
from wtforms.validators import Required, Email
from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy

bootstrap = Bootstrap( )
mail = Mail( )
db = SQLAlchemy( )

app = Flask( __name__ )

bootstrap.init_app( app )
mail.init_app( app )
db.init_app( app )

@app.route( "/" )
def hello( ):
	return "hello"

if __name__ == "__main__":
	app.run( )


