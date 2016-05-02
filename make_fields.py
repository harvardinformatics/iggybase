import sys
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
            print('%s is not an admin Model' % repr(mod))

    
mod_name = input_model()
table_object_id = sess.query(TableObject.id). \
    filter_by(name=eval(mod_name).__tablename__).one()[0]

id_nbr = int(sess.query(func.max(Field.name)).one()[0][1:]) + 1

insp = inspect(eval(mod_name))
for aa, col in insp.columns.items():

    field = Field(active=True,
                  name='F%06d' % (id_nbr),
                  display_name=col.name,
                  table_object_id=table_object_id,
                  primary_key=col.primary_key,
                  organization_id=1,
                  order=1,
                  description=col.name,
                  data_type_id=type_map[col.type.__visit_name__][0])

    length = getattr(col.type, 'length', None)
    if length:
        field.length = length
        


    if col.foreign_keys:
        fk = col.foreign_keys.pop()   ## only one foreign key.
        table, fld = fk.target_fullname.split('.')
        tobj = sess.query(TableObject).filter_by(name=table).one()
        field.foreign_key_table_object_id = getattr(tobj, fld, None)

        # In order to find the matching foreign_key_field_id, we need to
        # create a map in core because the sql driver chokes when looking for an
        # equivalent name in the field variable. So, a little trickiness
        fobj = sess.query(Field).filter_by(table_object_id=tobj.id). \
                filter_by(display_name='id').one()
        field.foreign_key_field_id = fobj.id
            
    sess.add(field)
    try:
        sess.commit()
    except:
        print('Failed to create field for %s' % col.name)

    id_nbr += 1


