import sys
from sqlalchemy.sql.functions import func
from run import make_app
from iggybase.database import db_session
from iggybase.mod_admin.models import *
from iggybase.mod_admin import models as adm_mods

app = make_app()        
sess = db_session        ## shorthand.


def input_role(where):
    """Get from or to role from the customer.
    """
    print()
    print('Which role to copy %s?' % where)
    for index, role in enumerate(roles):
        print(index+1, role.name)
    ans = input('1 - %d, which? ' % len(roles))
    try:
        role = roles[int(ans) - 1]
    except:
        print('Wrong answer. Frown....')
        sys.exit()
    return role

def do_you_want_message(from_role, to_role, role_models):
    print()
    msg = """Records for %s from the following tables will be duped 
to the role %s:""" \
        % (from_role.name, to_role.name)
    print(msg)
    print()
    for tab in role_mods:
        print(tab)
    print()
    do_you = "Do you want to continue? (y or n)? "
    ans = input(do_you)
    if ans != 'y':
        print('Bye...')
        sys.exit()


def new_record(model, rec, **kwargs):
    """Set the fields for a new record.
    Kwargs contain new values for fields.
    The fields: id, date_created, and date_modified are not copied

    Result is a dictionary.
    """
    names = [col[0] for col in eval(model).__table__.columns.items()]
    new_cols = dict((name, getattr(rec, name)) for name in names if name \
                    not in ['id', 'date_created', 'date_modified'])
    for k, val in kwargs.items():
        new_cols[k] = val
    return new_cols



# All the models that associate roles in mod_admin excluding Role itself. 
role_mods = [am for am in dir(adm_mods) if am.endswith('Role') and len(am) > len('Role')]

roles = sess.query(Role).order_by('name').all()

from_role = input_role('FROM')

roles.remove(from_role) # Remove from_role from choices.
to_role = input_role('TO')

do_you_want_message(from_role, to_role, role_mods)


for model in role_mods:
    recs = sess.query(eval(model)).filter_by(role_id=from_role.id). \
        filter_by(active=True).order_by('id')
    if recs.count() == 0:
        print('%s has 0 records. Nothing to dupe.' % model)
        continue
    
    initials = ''.join([c for c in model if c.isupper()]) # prepended to rec name.
    # The base number must guarantee uniqueness
    sequence  = sess.query(func.max(eval(model).id)).one()[0] + 3001
    import pdb
    pdb.set_trace()
    for indx, rec  in enumerate(recs):
        new_name = '%s%08d' % (initials, sequence+indx)
        if new_name == rec.name:    
            print("name mis-match, new_name == rec.name, %s" % new_name)
        new_rec = eval(model)()  # A new model instance.
        for k,v in new_record(model, rec, name=new_name).items():
            setattr(new_rec, k, v)  # Loading the new instance.
        sess.add(new_rec) # New object pending commit.
    sess.commit()   # Commit new records by model.
        


