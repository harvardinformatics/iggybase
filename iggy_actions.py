from actions import ActionManager, EmailAction
from flask import current_app
from database import db_session
from models import User

act_mgr = ActionManager(current_app, db_session)

msg = {
    'recipient': ('Reuven Koblick', 'reuven@koblick.com'),
    'bcc':'groovyroovy@gmail.com',
    'subject': 'Actions test',
    'body': {'text': 'This is a test.', 'context': {}} }

email_action = EmailAction('database', 'users', 'dirty', **msg)

rows = db_session.query(User).all()
email_action.load_params(tablename='users', fieldname='first_name',
                           keyname='id', rows=rows)



act_mgr.register_db_event(email_action)


