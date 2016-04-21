from sqlalchemy import inspect
from sqlalchemy.sql.functions import func
from iggybase.database import db_session as sess
from iggybase.admin.models import *
from iggybase.admin import models as adm_mods

type_map = {'boolean': (3, 'Boolean'),
            'datetime': (4, 'DateTime'),
            'integer': (1, 'Integer'),
            'password': (5, 'Password'),
            'string': (2, 'String'),
            'text': (7, 'Text')}

mod_chk = [mod for mod in dir(adm_mods) if mod[0].isupper()]
def input_model():
    while True:
        mod = input('Model name?  ')
        if mod in mod_chk:
            return mod
        else:
            print('%s is not an admin Model')

    
mod_name = input_model()
table_object_id = sess.query(TableObject.id). \
    filter_by(name=eval(mod_name).__tablename__).one()[0]

id_nbr = None
try:
    id_nbr = int(sess.query(func.max(eval(mod_name).name)).one()[0][1:]) + 1
except ValueError:
    print('Cannot create a name number, using the col.name instead')

insp = inspect(eval(mod_name))
for aa, col in insp.columns.items():
    field = Field(active=True,
                  field_name=col.name,
                  table_object_id=table_object_id,
                  primary_key=col.primary_key,
                  organization_id=1,
                  order=1,
                  description=col.name,
                  data_type_id=type_map[col.type.__visit_name__][0])
    length = getattr(col.type, 'length', None)
    if length:
        field.length = length
    field.name = 'F%06d' % (id_nbr) if id_nbr else col.name
    sess.add(field)
    try:
        sess.commit()
    except:
        print('error')


